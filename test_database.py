# test_database.py
import asyncio
from core.database import db


async def test_database():
    print("🧪 Testing database...")

    # Создаем таблицы
    await db.setup()
    print("✅ Tables created")

    # Тестируем вставку пользователя
    await db.execute_commit(
        "INSERT OR REPLACE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
        (123456, "test_user", "Test User")
    )
    print("✅ User inserted")

    # Проверяем что пользователь есть
    result = await db.execute("SELECT * FROM users WHERE user_id = ?", (123456,))
    if result:
        print(f"✅ User found: {dict(result[0])}")
    else:
        print("❌ User not found")

    await db.close()


if __name__ == "__main__":
    asyncio.run(test_database())