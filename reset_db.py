import asyncio
import os
from core.database import db


async def reset_database():
    """Сбрасывает базу данных PostgreSQL"""
    try:
        # Пересоздаем базу
        await db.setup()
        print("✅ База данных PostgreSQL создана")

        # Добавляем тестового админа (ЗАМЕНИ НА СВОЙ ID)
        await db.execute_commit("""
            INSERT INTO admins (user_id, username, role) 
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
        """, 2043400004, "Kaliev_Bekmurat", "admin")

        print("✅ Админ добавлен")
        print("🎯 База готова к использованию!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(reset_database())