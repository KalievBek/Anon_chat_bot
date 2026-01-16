import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import db


async def fix_broadcast_status_table():
    """Добавляет уникальное ограничение в таблицу broadcast_status"""
    try:
        await db.setup()

        # Добавляем уникальное ограничение
        await db.execute_commit("""
            ALTER TABLE broadcast_status 
            ADD CONSTRAINT unique_broadcast_user 
            UNIQUE (broadcast_id, user_id)
        """)

        print("✅ Уникальное ограничение добавлено в broadcast_status")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(fix_broadcast_status_table())