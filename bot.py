import os
import requests
import asyncio
from telegram import Bot

# 🔑 Ключи из Render Environment
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=BOT_TOKEN)

# ⚙️ Укажи свой Telegram ID (узнай через @userinfobot)
YOUR_CHAT_ID = 123456789  # ← замени на свой ID!

async def check_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()

            matches = data.get("response", [])
            if not matches:
                await bot.send_message(YOUR_CHAT_ID, "⚽ Сейчас нет активных матчей.")
            else:
                msg = "🔥 Текущие лайв-матчи:\n\n"
                for match in matches:
                    league = match["league"]["name"]
                    home = match["teams"]["home"]["name"]
                    away = match["teams"]["away"]["name"]
                    score_h = match["goals"]["home"]
                    score_a = match["goals"]["away"]
                    minute = match["fixture"]["status"]["elapsed"]
                    msg += f"🏆 {league}\n⚔️ {home} — {away}\n⏱️ {minute}'  |  {score_h}:{score_a}\n\n"

                await bot.send_message(YOUR_CHAT_ID, msg)

        except Exception as e:
            await bot.send_message(YOUR_CHAT_ID, f"❌ Ошибка: {e}")

        await asyncio.sleep(180)  # Проверять каждые 3 минуты

# 🚀 Запуск
if __name__ == "__main__":
    asyncio.run(check_live_matches())
