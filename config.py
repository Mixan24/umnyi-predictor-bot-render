import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = "db.sqlite3"

DEMO_MATCHES = [
    {"league":"Ла Лига","match":"Реал Мадрид — Барселона","attacks":175,"dangerous_attacks":122,"shots_on":6,"shots_total":14,"corners":7,"possession":59},
    {"league":"АПЛ","match":"Манчестер Сити — Ливерпуль","attacks":160,"dangerous_attacks":110,"shots_on":5,"shots_total":13,"corners":8,"possession":61},
    {"league":"Серия А","match":"Ювентус — Милан","attacks":132,"dangerous_attacks":90,"shots_on":3,"shots_total":10,"corners":4,"possession":52},
]
