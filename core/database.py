# core/database.py - НОРМАЛЬНАЯ ВЕРСИЯ
import aiosqlite
import logging
from .config import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "anon_chat.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """Подключается к базе данных"""
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
            logger.info("✅ SQLite database connection established")

    async def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            await self.conn.close()
            self.conn = None
            logger.info("✅ Database connection closed")

    async def execute(self, query: str, params: tuple = ()):
        """Выполняет SQL запрос и возвращает результат"""
        await self.connect()
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            raise

    async def execute_commit(self, query: str, params: tuple = ()):
        """Выполняет SQL запрос с коммитом"""
        await self.connect()
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                await self.conn.commit()
        except Exception as e:
            logger.error(f"❌ Database commit error: {e}")
            raise

    async def setup(self):
        """Создает все необходимые таблицы с нуля"""
        await self.connect()

        logger.info("🔄 Creating database tables...")

        # Таблица пользователей
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'menu',
                current_chat_id INTEGER DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица активных чатов
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS active_chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user1_id) REFERENCES users (user_id),
                FOREIGN KEY (user2_id) REFERENCES users (user_id)
            )
        """)

        # Индексы для быстрого поиска
        await self.execute_commit("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
        await self.execute_commit("CREATE INDEX IF NOT EXISTS idx_users_current_chat ON users(current_chat_id)")
        await self.execute_commit(
            "CREATE INDEX IF NOT EXISTS idx_active_chats_users ON active_chats(user1_id, user2_id)")

        logger.info("✅ Database tables created successfully")
        await self.close()


# Глобальный экземпляр базы данных
db = Database()