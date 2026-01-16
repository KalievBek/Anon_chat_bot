import asyncpg
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.conn = None
        # ТВОЙ ПАРОЛЬ
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:Kaliev200528@localhost:5432/anon_chat"
        )

    async def connect(self):
        if not self.conn:
            self.conn = await asyncpg.connect(self.db_url)
            logger.info("✅ Подключение к PostgreSQL установлено")

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None
            logger.info("✅ Подключение к PostgreSQL закрыто")

    async def execute(self, query: str, *params) -> List[asyncpg.Record]:
        """Выполняет запрос и возвращает результаты"""
        await self.connect()
        return await self.conn.fetch(query, *params)

    async def execute_commit(self, query: str, *params):
        """Выполняет запрос с коммитом"""
        await self.connect()
        await self.conn.execute(query, *params)  # ← УБРАЛ transaction()

    async def execute_scalar(self, query: str, *params):
        """Выполняет запрос и возвращает скалярное значение"""
        await self.connect()
        return await self.conn.fetchval(query, *params)

    async def setup(self):
        """Создает все необходимые таблицы"""
        await self.connect()

        # Пользователи
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                status TEXT DEFAULT 'menu',
                current_chat_id BIGINT,
                gender TEXT DEFAULT 'not_specified',
                age INTEGER,
                interests TEXT DEFAULT '',
                rating REAL DEFAULT 5.0,
                total_chats INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Активные поиски
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS search_queue (
                user_id BIGINT PRIMARY KEY,
                gender_preference TEXT DEFAULT 'any',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Чаты
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id SERIAL PRIMARY KEY,
                user1_id BIGINT NOT NULL,
                user2_id BIGINT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (user2_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Сообщения
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id SERIAL PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                text TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Рассылки
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                broadcast_id SERIAL PRIMARY KEY,
                admin_id BIGINT NOT NULL,
                message_text TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                file_id TEXT,
                filters JSONB DEFAULT '{}',
                sent_count INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            )
        """)

        # Статусы доставки рассылок
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS broadcast_status (
                status_id SERIAL PRIMARY KEY,
                broadcast_id INTEGER,
                user_id BIGINT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (broadcast_id) REFERENCES broadcasts(broadcast_id) ON DELETE CASCADE
            )
        """)

        # Админы и модераторы
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'moderator',
                permissions JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 🔧 ДОБАВЛЕННЫЕ ТАБЛИЦЫ ДЛЯ АДМИН-ПАНЕЛИ

        # Забаненные пользователи
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id BIGINT PRIMARY KEY,
                reason TEXT NOT NULL,
                banned_by BIGINT NOT NULL,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (banned_by) REFERENCES admins(user_id)
            )
        """)

        # Жалобы пользователей
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id SERIAL PRIMARY KEY,
                reporter_id BIGINT NOT NULL,
                reported_user_id BIGINT NOT NULL,
                reason TEXT NOT NULL,
                chat_id INTEGER,
                message_text TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES users(user_id),
                FOREIGN KEY (reported_user_id) REFERENCES users(user_id),
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
        """)

        # Системные уведомления для админов
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS admin_notifications (
                notification_id SERIAL PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Настройки бота
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by BIGINT,
                FOREIGN KEY (updated_by) REFERENCES admins(user_id)
            )
        """)

        # История действий администраторов
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS admin_actions (
                action_id SERIAL PRIMARY KEY,
                admin_id BIGINT NOT NULL,
                action_type TEXT NOT NULL,
                target_id BIGINT,
                details JSONB DEFAULT '{}',
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES admins(user_id)
            )
        """)

        # Статистика по дням
        await self.execute_commit("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                stat_date DATE PRIMARY KEY,
                new_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                total_chats INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                avg_chat_duration INTEGER DEFAULT 0,
                avg_rating REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Добавляем тестового админа (ЗАМЕНИ НА СВОЙ USER_ID)
        await self.execute_commit("""
            INSERT INTO admins (user_id, username, role) 
            VALUES (2043400004, 'Kaliev_Bekmurat', 'superadmin')
            ON CONFLICT (user_id) DO NOTHING
        """)

        # Добавляем базовые настройки бота
        await self.execute_commit("""
            INSERT INTO bot_settings (key, value, description) VALUES
            ('max_messages_per_minute', '10', 'Максимальное количество сообщений в минуту'),
            ('search_timeout', '60', 'Таймаут поиска в секундах'),
            ('min_rating_for_search', '3', 'Минимальный рейтинг для поиска'),
            ('welcome_message', 'Добро пожаловать!', 'Приветственное сообщение'),
            ('auto_ban_reports', '5', 'Автобан после N жалоб')
            ON CONFLICT (key) DO NOTHING
        """)

        # Создаем индексы для производительности
        await self.create_indexes()

        logger.info("✅ База данных PostgreSQL настроена")

    async def create_indexes(self):
        """Создает индексы для оптимизации запросов"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)",
            "CREATE INDEX IF NOT EXISTS idx_users_gender ON users(gender)",
            "CREATE INDEX IF NOT EXISTS idx_chats_user1 ON chats(user1_id)",
            "CREATE INDEX IF NOT EXISTS idx_chats_user2 ON chats(user2_id)",
            "CREATE INDEX IF NOT EXISTS idx_chats_ended ON chats(ended_at)",
            "CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at)",
            "CREATE INDEX IF NOT EXISTS idx_search_queue_gender ON search_queue(gender_preference)",

            # 🔧 НОВЫЕ ИНДЕКСЫ ДЛЯ АДМИНКИ
            "CREATE INDEX IF NOT EXISTS idx_banned_users_expires ON banned_users(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)",
            "CREATE INDEX IF NOT EXISTS idx_reports_reported_user ON reports(reported_user_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_admin_notifications_read ON admin_notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_admin_notifications_priority ON admin_notifications(priority)",
            "CREATE INDEX IF NOT EXISTS idx_admin_actions_admin ON admin_actions(admin_id)",
            "CREATE INDEX IF NOT EXISTS idx_admin_actions_created ON admin_actions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(stat_date)"
        ]

        for index_sql in indexes:
            try:
                await self.execute_commit(index_sql)
            except Exception as e:
                logger.warning(f"Не удалось создать индекс: {e}")

    async def check_table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы"""
        try:
            result = await self.execute_scalar("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table_name)
            return result
        except Exception as e:
            logger.error(f"Ошибка проверки таблицы {table_name}: {e}")
            return False


# Глобальный экземпляр
db = Database()