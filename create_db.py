import asyncio
from core.database import db


async def create_database():
    """Просто создает базу данных"""
    await db.setup()
    print("✅ База данных создана!")

    # Проверим таблицы
    tables = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("📊 Созданные таблицы:")
    for table in tables:
        print(f"  - {table['name']}")


asyncio.run(create_database())