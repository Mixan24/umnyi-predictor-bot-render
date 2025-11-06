import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🌐 Фейковый веб-сервер, чтобы Render не завершал процесс
def keep_alive():
    try:
        PORT = int(os.getenv("PORT", 10000))
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"🌐 Dummy server running on port {PORT}")
            httpd.serve_forever()
    except OSError:
        print("⚠️ Порт уже занят, сервер уже работает.")

threading.Thread(target=keep_alive, daemon=True).start()

# 🔑 Переменные окружения
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=BOT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()
active_users = set()
last_probabilities = {}  # храним изменения по матчам

# ⚽ Расчёт вероятности гола
def calculate_goal_probability(stats):
    try:
        attacks = stats.get("attacks", 0)
        shots = stats.get("shots_on_target", 0)
        dangerous = stats.get("dangerous_attacks", 0)
        possession = stats.get("possession", 0)
        pressure = (shots * 4 + attacks * 0.5 + dangerous * 0.8 + possession * 0.2) / 3
        return round(min(pressure, 100), 1)
    except Exception:
        return 0.0

# 👋 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    name = update.effective_user.first_name
    active_users.add(chat_id)
    await update.message.reply_text(
        f"👋 Привет, {name}!\n"
        f"Ты подключён к системе ⚽ прогнозов.\n"
        f"Я сообщу, когда вероятность гола превысит 80 %, "
        f"и даже заранее — если давление растёт 📈"
    )
    print(f"[✅] Подключён пользователь: {chat_id} ({name})")

# 🔍 Анализ лайв-матчей
async def analyze_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}
    alerted = set()

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()
            matches = data.get("response", [])

            if not matches:
                for user in active_users:
                    await bot.send_message(user, "⚽ Сейчас нет активных матчей.")
            else:
                for match in matches:
                    league = match["league"]["name"]
                    home = match["teams"]["home"]["name"]
                    away = match["teams"]["away"]["name"]
                    minute = match["fixture"]["status"]["elapsed"]
                    stats = match.get("statistics", [])

                    if not stats:
                        continue

                    team_stats = stats[0]["statistics"] if isinstance(stats[0], dict) else []
                    values = {
                        "shots_on_target": next((x["value"] for x in team_stats if x["type"] == "Shots on Goal"), 0),
                        "attacks": next((x["value"] for x in team_stats if x["type"] == "Attacks"), 0),
                        "dangerous_attacks": next((x["value"] for x in team_stats if x["type"] == "Dangerous Attacks"), 0),
                        "possession": int(str(next((x["value"] for x in team_stats if x["type"] == "Ball Possession"), "0")).replace("%", ""))
                    }

                    prob = calculate_goal_probability(values)
                    key = f"{home}-{away}"

                    # 📈 Раннее предупреждение — если рост давления > 10 %
                    last = last_probabilities.get(key, 0)
                    if 60 <= last < prob and prob - last >= 10:
                        for user in active_users:
                            await bot.send_message(
                                user,
                                f"📈 Давление растёт!\n"
                                f"⚔️ {home} — {away}\n"
                                f"⏱️ {minute}' минута\n"
                                f"📊 Вероятность: {last}% → {prob}%"
                            )

                    last_probabilities[key] = prob

                    # ⚽ Основное предупреждение (>80 %)
                    if prob >= 80 and key not in alerted:
                        msg = (
                            f"⚽ Возможен гол!\n"
                            f"🏆 {league}\n"
                            f"⚔️ {home} — {away}\n"
                            f"⏱️ {minute}' минута\n"
                            f"📊 Вероятность: {prob}%"
                        )
                        for user in active_users:
                            await bot.send_message(user, msg)
                        alerted.add(key)

        except Exception as e:
            for user in active_users:
                await bot.send_message(user, f"❌ Ошибка анализа: {e}")

        await asyncio.sleep(120)  # проверка каждые 2 мин

# 🚀 Запуск
async def run_bot():
    app.add_handler(CommandHandler("start", start))
    asyncio.create_task(analyze_live_matches())
    print("🤖 Бот запущен и ждёт /start")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run_bot())
