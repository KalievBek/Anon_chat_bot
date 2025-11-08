# main.py - ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ SQLite
import asyncio
import logging
import os
import sys

from core.bot import dp, bot
from core.database import db
from handlers import command_router, callback_router, message_router, reply_router, chat_handlers

# Создаем папку для логов если её нет
os.makedirs('logs', exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    try:
        # 1. Настройка базы данных SQLite
        logger.info("🔄 Настройка базы данных SQLite...")
        await db.setup()
        logger.info("✅ SQLite database setup complete.")

        # Проверяем структуру таблицы (SQLite версия)
        await db.connect()
        tables = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        logger.info(f"📊 Таблицы в базе: {[table['name'] for table in tables]}")

        if tables and any(table['name'] == 'users' for table in tables):
            # Для SQLite проверяем колонки через PRAGMA
            columns = await db.execute("PRAGMA table_info(users)")
            column_names = [column['name'] for column in columns]
            logger.info(f"📋 Колонки в таблице users: {column_names}")

            # Проверяем наличие обязательных колонок
            required_columns = ['user_id', 'status']
            for col in required_columns:
                if col not in column_names:
                    logger.error(f"❌ Отсутствует обязательная колонка: {col}")
        else:
            logger.error("❌ Таблица 'users' не найдена!")

        await db.close()

        # 2. Подключение роутеров
        dp.include_router(command_router)
        dp.include_router(callback_router)
        dp.include_router(message_router)
        dp.include_router(reply_router)
        dp.include_router(chat_handlers.router)  # Добавьте эту строку
        # 3. Запуск бота
        logger.info("🚀 Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("✅ Бот успешно запущен!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        raise
    finally:
        await db.close()
        logger.info("🛑 Bot stopped.")


if __name__ == "__main__":
    try:
        # Проверяем наличие токена бота
        if not hasattr(bot, 'token') or not bot.token:
            logger.error("❌ Токен бота не найден! Проверьте настройки.")
            sys.exit(1)

        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}", exc_info=True)
        print(f"❌ Произошла ошибка: {e}")