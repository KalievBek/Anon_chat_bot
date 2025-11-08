# core/database.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import aiosqlite
import logging
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
            logger.info("Database connection established")

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    async def execute(self, query: str, params: tuple = ()):
        await self.connect()
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, params)
            result = await cursor.fetchall()
        return result

    async def execute_commit(self, query: str, params: tuple = ()):
        await self.connect()
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, params)
            await self.conn.commit()

    async def setup(self):
        """Создает таблицы при первом запуске и проверяет структуру."""
        await self.connect()

        # Создаем таблицу пользователей
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                status TEXT NOT NULL DEFAULT 'menu',
                current_chat_id INTEGER DEFAULT NULL 
            )
        """)

        # Проверяем существование колонки status и добавляем если нужно
        try:
            await self.execute("SELECT status FROM users LIMIT 1")
            logger.info("Column 'status' exists")
        except aiosqlite.OperationalError as e:
            if "no such column" in str(e):
                logger.info("Adding column 'status' to users table")
                await self.execute_commit("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'menu'")
            else:
                raise e

        # Проверяем существование колонки current_chat_id
        try:
            await self.execute("SELECT current_chat_id FROM users LIMIT 1")
            logger.info("Column 'current_chat_id' exists")
        except aiosqlite.OperationalError as e:
            if "no such column" in str(e):
                logger.info("Adding column 'current_chat_id' to users table")
                await self.execute_commit("ALTER TABLE users ADD COLUMN current_chat_id INTEGER DEFAULT NULL")
            else:
                raise e

        logger.info("Database setup completed successfully")
        await self.close()


# Глобальный экземпляр базы данных
db = Database()