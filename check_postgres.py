# check_postgres.py
import asyncio
import logging
from core.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_postgres():
    """Тестирует подключение к PostgreSQL"""
    try:
        logger.info("🔍 Testing PostgreSQL connection...")

        # Проверяем подключение
        await db.connect()

        # Проверяем версию PostgreSQL
        result = await db.execute("SELECT version()")
        logger.info(f"📊 PostgreSQL version: {result[0]['version']}")

        # Проверяем таблицы
        tables = await db.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        logger.info(f"📋 Available tables: {[t['table_name'] for t in tables]}")

        await db.close()
        logger.info("✅ PostgreSQL connection test successful!")

    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_postgres())