import os
import requests
import asyncio
from telegram import Bot

# 🔑 Токены
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=BOT_TOKEN)

# 💬 Укажи свой Telegram ID (узнай через бота @userinfobot)
YOUR_CHAT_ID = 123456789  # 👉 замени на свой ID

# 🔍 Основная функция анализа
async def analyze_live_matches():
    url_live = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    while True:
        try:
            live = requests.get(url_live, headers=headers).json()
            for match in live.get("response", []):
                fixture_id = match["fixture"]["id"]
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
                score = f"{match['goals']['home']}:{match['goals']['away']}"

                # Запрос статистики матча
                stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
                stats = requests.get(stats_url, headers=headers).json()

                if not stats["response"]:
                    continue

                for team_stats in stats["response"]:
                    team_name = team_stats["team"]["name"]
                    data = {s["type"]: s["value"] for s in team_stats["statistics"]}

                    # 📊 Извлекаем ключевые метрики
                    shots_on = data.get("Shots on Goal", 0) or 0
                    dangerous_attacks = data.get("Dangerous Attacks", 0) or 0
                    possession = int((data.get("Ball Possession", "0%") or "0%").replace("%", ""))

                    # 🧠 Простая формула вероятности гола
                    prob = (shots_on * 6 + dangerous_attacks * 0.6 + possession * 0.5) / 10

                    if prob > 80:
                        await bot.send_message(
                            chat_id=YOUR_CHAT_ID,
                            text=(
                                f"⚡ Возможен гол в ближайшие минуты!\n"
                                f"Матч: {home} — {away}\n"
                                f"Команда: {team_name}\n"
                                f"Счёт: {score}\n"
                                f"Вероятность гола: {prob:.1f}%"
                            )
                        )
                        await asyncio.sleep(30)

        except Exception as e:
            print("Ошибка анализа:", e)

        await asyncio.sleep(120)  # Проверка каждые 2 минуты

# 🚀 Запуск
if __name__ == "__main__":
    asyncio.run(analyze_live_matches())
