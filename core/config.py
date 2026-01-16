import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    DB_PATH: str = "anon_chat.db"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# Проверяем токен
if not os.path.exists('.env'):
    print("⚠️ Файл .env не найден! Создайте его с BOT_TOKEN=your_token")

settings = Settings()

if not settings.BOT_TOKEN:
    print("❌ BOT_TOKEN не найден! Убедитесь, что он указан в файле .env")
    exit(1)