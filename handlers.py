from aiogram import types
from config import DEMO_MATCHES
from predictor import calculate_goal_probability

async def start_handler(message: types.Message):
    await message.answer(
        "🤖 Привет! Я бот-прогнозист ⚽\n\n"
        "Я анализирую матчи и оцениваю вероятность гола.\n\n"
        "Команды:\n• /live — текущие прогнозы\n• /help — справка"
    )

async def help_handler(message: types.Message):
    await message.answer(
        "📘 Справка:\nЯ показываю вероятность гола на основе активности команд.\n"
        "Данные демо, обновляются каждые 3 минуты автоматически."
    )

async def live_handler(message: types.Message):
    text = "⚽ <b>Текущие прогнозы (демо)</b>\n\n"
    for m in DEMO_MATCHES:
        prob = calculate_goal_probability(m)
        text += (
            f"🏆 <b>{m['league']}</b>\n{m['match']}\n"
            f"Атаки: {m['attacks']} | Опасные: {m['dangerous_attacks']}\n"
            f"Удары: {m['shots_total']} (в створ: {m['shots_on']}) | Угловые: {m['corners']}\n"
            f"Владение: {m['possession']}%\n"
            f"🔮 Вероятность гола: <b>{prob}%</b>\n\n"
        )
    await message.answer(text, parse_mode="HTML")
