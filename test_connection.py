import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import db


async def test_postgres():
    print("🔍 Тестируем подключение к PostgreSQL...")
    try:
        await db.connect()
        print("✅ Подключение к PostgreSQL успешно!")

        # Создаем таблицы
        await db.setup()
        print("✅ Таблицы созданы!")

        # Проверяем таблицы
        tables = await db.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)

        print("📊 Таблицы в базе:")
        for table in tables:
            print(f"   - {table['table_name']}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверь запущен ли PostgreSQL (Пуск → PostgreSQL 17)")
        print("2. Проверь пароль в database.py")
        print("3. Проверь имя базы 'anon_chat' в PGAdmin")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(test_postgres())