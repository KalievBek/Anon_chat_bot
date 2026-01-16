from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения. Проверь файл .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()