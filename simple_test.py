# simple_test.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def test():
    try:
        print("🔍 Testing PostgreSQL connection...")
        print(f"User: {os.getenv('POSTGRES_USER')}")
        print(f"Database: {os.getenv('POSTGRES_DB')}")

        conn = await asyncpg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )

        version = await conn.fetchval('SELECT version()')
        print(f"✅ SUCCESS! PostgreSQL version: {version}")

        # Проверим таблицы
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print(f"📊 Tables: {[t['table_name'] for t in tables]}")

        await conn.close()

    except Exception as e:
        print(f"❌ ERROR: {e}")


asyncio.run(test())