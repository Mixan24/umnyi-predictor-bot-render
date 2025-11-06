# ⚙️ Этот файл безопасен — токен берётся из Render или .env

import os
from dotenv import load_dotenv

# Загружаем .env (только при локальном запуске)
load_dotenv()

# Берём значения из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))
