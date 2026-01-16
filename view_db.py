import asyncio
import aiosqlite


async def view_database():
    """Показывает содержимое базы"""
    async with aiosqlite.connect("anon_chat.db") as conn:
        conn.row_factory = aiosqlite.Row

        # Показать все таблицы
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()

        print("📋 Таблицы в базе:")
        for table in tables:
            print(f"\n📊 Таблица: {table['name']}")

            # Показать содержимое каждой таблицы
            cursor = await conn.execute(f"SELECT * FROM {table['name']} LIMIT 5")
            rows = await cursor.fetchall()

            if rows:
                print(f"   Данные ({len(rows)} записей):")
                for row in rows:
                    print(f"   - {dict(row)}")
            else:
                print("   (пусто)")


asyncio.run(view_database())