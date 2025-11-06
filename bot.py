import os
import requests
import asyncio
import threading
import http.server
import socketserver
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🌀 Разрешаем повторные event-loop (нужно для Render)
nest_asyncio.apply()

# 🌐 Поддержка активности Render (чтобы не засыпал)
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

# ✅ Основное приложение Telegram
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Активные пользователи
active_users = set()
last_probabilities = {}

# ⚽ Функция расчёта вероятности
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
        f"и заранее — если давление растёт 📈"
    )
    print(f"[✅] Подключён пользователь: {chat_id} ({name})")

# 🔍 Основной анализ матчей
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
                    await app.bot.send_message(user, "⚽ Сейчас нет активных матчей.")
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

                    # 📈 Рост давления
                    last = last_probabilities.get(key, 0)
                    if 60 <= last < prob and prob - last >= 10:
                        for user in active_users:
                            await app.bot.send_message(
                                user,
                                f"📈 Давление растёт!\n"
                                f"⚔️ {home} — {away}\n"
                                f"⏱️ {minute}' минута\n"
                                f"📊 Вероятность: {last}% → {prob}%"
                            )

                    last_probabilities[key] = prob

                    # ⚽ Возможен гол
                    if prob >= 80 and key not in alerted:
                        msg = (
                            f"⚽ Возможен гол!\n"
                            f"🏆 {league}\n"
                            f"⚔️ {home} — {away}\n"
                            f"⏱️ {minute}' минута\n"
                            f"📊 Вероятность: {prob}%"
                        )
                        for user in active_users:
                            await app.bot.send_message(user, msg)
                        alerted.add(key)

        except Exception as e:
            print(f"Ошибка анализа: {e}")
        await asyncio.sleep(120)

# 🚀 Запуск
async def main():
    app.add_handler(CommandHandler("start", start))
    asyncio.create_task(analyze_live_matches())
    print("🤖 Бот запущен и ждёт /start")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    print("🚀 Запуск умного футбольного прогнозиста...")
    asyncio.run(main())
