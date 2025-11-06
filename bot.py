import os
import logging
import random
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🌿 Логи
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔑 Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL", "https://umnyi-fermer-proxy.onrender.com")

# ⚽ Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Привет! Я футбольный бот Умного фермера!\n"
        "Напиши название двух команд — и я дам прогноз на матч.\n\n"
        "Пример: Барселона Реал"
    )

# 🎯 Генератор простого прогноза (если без ИИ)
def simple_prediction(team1, team2):
    outcomes = [
        f"Победит {team1} ✅",
        f"Победит {team2} ⚽",
        "Ничья 🤝",
        f"{team1} забьёт первым ⚡",
        f"{team2} удивит и выиграет в концовке 🔥"
    ]
    confidence = random.randint(55, 90)
    return f"Прогноз: {random.choice(outcomes)}\nВероятность: {confidence}%"

# 💬 Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await update.message.reply_text("🤔 Анализирую матч...")

    try:
        # Разбиваем сообщение на команды
        words = text.split()
        if len(words) < 2:
            await update.message.reply_text("❗ Введите две команды, например: Барселона Реал")
            return

        team1, team2 = words[0], words[1]

        # 🧠 Запрос через OpenAI-прокси
        response = requests.post(
            f"{PROXY_URL}/ask",
            json={
                "prompt": f"Сделай краткий прогноз на футбольный матч {team1} против {team2}. "
                          "Укажи вероятного победителя и счёт.",
                "key": OPENAI_API_KEY
            },
            timeout=30
        )

        if response.status_code == 200:
            answer = response.json().get("reply")
            if answer:
                await update.message.reply_text(f"⚽ {answer}")
            else:
                await update.message.reply_text(simple_prediction(team1, team2))
        else:
            await update.message.reply_text(simple_prediction(team1, team2))

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("⚠️ Не удалось получить прогноз. Пробую без ИИ...")
        try:
            words = text.split()
            if len(words) >= 2:
                await update.message.reply_text(simple_prediction(words[0], words[1]))
            else:
                await update.message.reply_text("Введите две команды, например: Барселона Реал")
        except Exception as inner_e:
            logging.error(inner_e)
            await update.message.reply_text("🚧 Ошибка при обработке запроса.")

# 🚀 Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Футбольный бот запущен!")
    app.run_polling()
