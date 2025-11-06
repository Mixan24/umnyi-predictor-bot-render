import os
import logging
import requests
from datetime import date
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# 🌿 Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔑 Ключи и токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN не найден в переменных окружения.")
if not FOOTBALL_API_KEY:
    raise ValueError("❌ FOOTBALL_DATA_API_KEY не найден в переменных окружения.")

# 🌍 URL API
BASE_URL = "https://api.football-data.org/v4/matches"

# 👋 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚽ Привет! Это футбольный бот от Умного Фермера.\n\n"
        "📋 Команды:\n"
        "• /live — показать матчи, которые идут прямо сейчас\n"
        "• /today — показать все матчи на сегодня\n"
        "• /help — помощь"
    )
    await update.message.reply_text(text)

# 🆘 Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ Используй /live для лайв-матчей и /today для матчей на сегодня ⚽")

# 📺 LIVE-матчи
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        data = response.json().get("matches", [])
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("🚧 Ошибка при получении данных от Football API.")
        return

    live_games = []
    for m in data:
        if m.get("status") in ("IN_PLAY", "PAUSED"):
            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]
            score = m["score"]["fullTime"]
            live_games.append(f"{home} {score['home']} : {score['away']} {away}")

    if live_games:
        text = "📺 <b>LIVE-матчи:</b>\n\n" + "\n".join(live_games)
        await update.message.reply_text(text, parse_mode="HTML")
    else:
        await update.message.reply_text("⚽ Сейчас нет активных матчей.")

# 📅 Матчи на сегодня
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    today_str = date.today().isoformat()

    try:
        response = requests.get(f"{BASE_URL}?dateFrom={today_str}&dateTo={today_str}", headers=headers, timeout=10)
        data = response.json().get("matches", [])
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("🚧 Ошибка при получении данных от Football API.")
        return

    if not data:
        await update.message.reply_text("📭 Сегодня нет запланированных матчей.")
        return

    lines = []
    for m in data:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        status = m["status"]
        time = m.get("utcDate", "")[11:16]
        lines.append(f"🕒 {time} — {home} 🆚 {away} ({status})")

    text = "📅 <b>Матчи на сегодня:</b>\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="HTML")

# 🚀 Запуск
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("live", live))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))

    logging.info("✅ Бот запущен и слушает команды...")
    app.run_polling()

if __name__ == "__main__":
    main()
