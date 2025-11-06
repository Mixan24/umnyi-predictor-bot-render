import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Bot

# 🌐 Фейковый сервер, чтобы Render не завершал процесс
def keep_alive():
    PORT = int(os.getenv("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌐 Dummy server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# 🔑 Переменные окружения
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=BOT_TOKEN)

# 🧍 Укажи свой Telegram ID
YOUR_CHAT_ID = 123456789  # ← замени на свой ID!

# ⚽ Функция подсчёта вероятности гола
def calculate_goal_probability(stats):
    try:
        attacks = stats.get("attacks", 0)
        shots = stats.get("shots_on_target", 0)
        dangerous = stats.get("dangerous_attacks", 0)
        possession = stats.get("possession", 0)

        # Условная модель давления (0–100)
        pressure = (shots * 4 + attacks * 0.5 + dangerous * 0.8 + possession * 0.2) / 3
        return min(round(pressure, 1), 100)
    except Exception:
        return 0.0

async def analyze_live_matches():
    fixtures_url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        "x-apisports-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    alerted_matches = set()

    while True:
        try:
            response = requests.get(fixtures_url, headers=headers, timeout=30)
            data = response.json()
            matches = data.get("response", [])

            if not matches:
                print("⚽ Нет активных матчей.")
            else:
                for match in matches:
                    fixture_id = match["fixture"]["id"]
                    league = match["league"]["name"]
                    home = match["teams"]["home"]["name"]
                    away = match["teams"]["away"]["name"]
                    minute = match["fixture"]["status"]["elapsed"]

                    # Запрашиваем статистику отдельно
                    stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
                    stats_resp = requests.get(stats_url, headers=headers, timeout=30)
                    stats_data = stats_resp.json().get("response", [])

                    if not stats_data:
                        continue

                    # Берём статистику для домашней команды
                    team_stats = stats_data[0]["statistics"]
                    values = {
                        "shots_on_target": next((x["value"] for x in team_stats if x["type"] == "Shots on Goal"), 0),
                        "attacks": next((x["value"] for x in team_stats if x["type"] == "Attacks"), 0),
                        "dangerous_attacks": next((x["value"] for x in team_stats if x["type"] == "Dangerous Attacks"), 0),
                        "possession": int(str(next((x["value"] for x in team_stats if x["type"] == "Ball Possession"), "0")).replace("%",""))
                    }

                    probability = calculate_goal_probability(values)
                    key = f"{home}-{away}"

                    if probability >= 80 and key not in alerted_matches:
                        msg = (
                            f"⚽ Возможен гол!\n"
                            f"🏆 {league}\n"
                            f"⚔️ {home} — {away}\n"
                            f"⏱️ {minute}' минута\n"
                            f"📊 Вероятность гола: {probability}%"
                        )
                        await bot.send_message(YOUR_CHAT_ID, msg)
                        alerted_matches.add(key)

        except Exception as e:
            print("❌ Ошибка анализа:", e)

        await asyncio.sleep(120)  # каждые 2 минуты

# 🚀 Запуск
if __name__ == "__main__":
    asyncio.run(analyze_live_matches())
