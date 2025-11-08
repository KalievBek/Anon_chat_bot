# core/config.py
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения!")

    # Используем SQLite
    DB_PATH: str = "anon_chat.db"


settings = Settings()