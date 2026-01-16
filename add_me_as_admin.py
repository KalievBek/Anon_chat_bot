import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import db


async def add_admin():
    """Добавляет пользователя как администратора"""
    try:
        # ТВОИ ДАННЫЕ
        YOUR_USER_ID = 2043400004  # 👈 Твой user_id
        YOUR_USERNAME = "Kaliev_Bekmurat"  # 👈 Твой username

        print(f"🔄 Добавляем пользователя {YOUR_USER_ID} как админа...")

        await db.execute_commit("""
            INSERT INTO admins (user_id, username, role) 
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
            username = $2,
            role = $3
        """, YOUR_USER_ID, YOUR_USERNAME, "superadmin")

        print(f"✅ Ты добавлен как админ! ID: {YOUR_USER_ID}")

        # Проверим
        admin = await db.execute("SELECT * FROM admins WHERE user_id = $1", YOUR_USER_ID)
        if admin:
            print("✅ Проверка: ты в списке админов!")
            admin_data = dict(admin[0])
            print(
                f"📋 Данные: ID={admin_data['user_id']}, Username=@{admin_data['username']}, Role={admin_data['role']}")
        else:
            print("❌ Что-то пошло не так...")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(add_admin())