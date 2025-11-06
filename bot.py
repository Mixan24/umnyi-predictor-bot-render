import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🌿 Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🔑 Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL", "https://umnyi-fermer-proxy.onrender.com")

# 👋 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 Привет! Я бот Умного фермера. Задай вопрос — я помогу советом.")

# 💬 Ответы на сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🤔 Думаю над ответом...")

    try:
        response = requests.post(
            f"{PROXY_URL}/ask",
            json={"prompt": user_text, "key": OPENAI_API_KEY},
            timeout=30
        )
        if response.status_code == 200:
            answer = response.json().get("reply", "❌ Не удалось получить ответ.")
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text("⚠️ Ошибка при обращении к серверу.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("🚧 Что-то пошло не так, попробуй позже.")

# 🚀 Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен и готов к работе!")
    app.run_polling()
