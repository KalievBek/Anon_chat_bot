# core/bot.py
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from .config import settings

# Инициализируем Bot
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Инициализируем Dispatcher
dp = Dispatcher()