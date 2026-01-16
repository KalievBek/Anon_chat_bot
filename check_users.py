import asyncio
import aiosqlite


async def check_users():
    async with aiosqlite.connect("anon_chat.db") as conn:
        conn.row_factory = aiosqlite.Row

        # Проверим пользователей
        cursor = await conn.execute("SELECT * FROM users")
        users = await cursor.fetchall()

        print(f"👥 Пользователей в базе: {len(users)}")
        for user in users:
            print(f"   - ID: {user['user_id']}, Имя: {user['first_name']}, Username: @{user['username']}")


asyncio.run(check_users())