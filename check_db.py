import asyncio
import aiosqlite


async def check_chats_and_messages():
    async with aiosqlite.connect("anon_chat.db") as conn:
        conn.row_factory = aiosqlite.Row

        # Проверим чаты
        cursor = await conn.execute("SELECT * FROM chats")
        chats = await cursor.fetchall()
        print(f"💬 Чатов в базе: {len(chats)}")
        for chat in chats:
            print(f"   - Чат {chat['chat_id']}: {chat['user1_id']} ↔ {chat['user2_id']} ({chat['started_at']})")

        # Проверим сообщения
        cursor = await conn.execute("SELECT * FROM messages")
        messages = await cursor.fetchall()
        print(f"✉️ Сообщений в базе: {len(messages)}")
        for msg in messages[:5]:  # Покажем первые 5
            print(f"   - Сообщение {msg['message_id']}: пользователь {msg['user_id']} в чате {msg['chat_id']}")


asyncio.run(check_chats_and_messages())