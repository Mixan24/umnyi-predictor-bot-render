import asyncio, schedule, time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiosqlite
from config import BOT_TOKEN, DB_PATH
from handlers import start_handler, help_handler, live_handler
from predictor import calculate_goal_probability
from config import DEMO_MATCHES

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await start_handler(msg)

@dp.message_handler(commands=["help"])
async def help(msg: types.Message):
    await help_handler(msg)

@dp.message_handler(commands=["live"])
async def live(msg: types.Message):
    await live_handler(msg)

@dp.message_handler(commands=["id"])
async def get_id(msg: types.Message):
    await msg.answer(f"🧩 Твой Telegram ID: <b>{msg.from_user.id}</b>", parse_mode="HTML")

async def auto_notify():
    text = "⚽ <b>Автообновление прогнозов</b>\n\n"
    for m in DEMO_MATCHES:
        prob = calculate_goal_probability(m)
        text += (
            f"{m['league']}: {m['match']} — 🔮 {prob}% вероятность гола\n"
        )

    YOUR_CHAT_ID = None
    if YOUR_CHAT_ID:
        try:
            await bot.send_message(YOUR_CHAT_ID, text, parse_mode="HTML")
        except Exception as e:
            print(f"⚠️ Ошибка автообновления: {e}")

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

async def on_startup(_):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, first_name TEXT)")
        await db.commit()
    schedule.every(3).minutes.do(lambda: asyncio.create_task(auto_notify()))
    asyncio.create_task(asyncio.to_thread(schedule_loop))
    print("✅ Бот запущен (Render) — обновление каждые 3 минуты!")

if __name__ == "__main__":
    asyncio.run(executor.start_polling(dp, skip_updates=True, on_startup=on_startup))
