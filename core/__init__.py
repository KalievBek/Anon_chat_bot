from aiogram import Bot, Dispatcher
from .config import settings  # ← ИМПОРТИРУЕМ settings, а не config
from .database import db

# Создаем экземпляры бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

__all__ = ['bot', 'dp', 'db', 'settings']  # ← settings вместо config