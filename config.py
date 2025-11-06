# ⚙️ Этот файл безопасный — токен берётся из Render или .env
import os
from dotenv import load_dotenv

# Загружаем .env для локального теста
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))
