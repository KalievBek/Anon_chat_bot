# core/bot.py
from aiogram import Bot, Dispatcher
from .config import settings

# Инициализируем Bot (простой вариант)
bot = Bot(token=settings.BOT_TOKEN)

# Инициализируем Dispatcher
dp = Dispatcher()