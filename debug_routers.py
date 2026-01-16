# debug_routers.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import dp, bot, db
from admin import admin_router
from broadcasts import broadcast_router
from handlers import commands_router, messages_router, callbacks_router


async def debug_routers():
    await db.setup()

    dp.include_router(broadcast_router)
    dp.include_router(admin_router)
    dp.include_router(commands_router)
    dp.include_router(messages_router)
    dp.include_router(callbacks_router)

    print("🔍 СТАТУС РОУТЕРОВ:")
    routers = [
        ("broadcast_router", broadcast_router),
        ("admin_router", admin_router),
        ("commands_router", commands_router),
        ("messages_router", messages_router),
        ("callbacks_router", callbacks_router)
    ]

    for name, router in routers:
        message_handlers = len(router.message.handlers)
        callback_handlers = len(router.callback_query.handlers)
        print(f"📋 {name}: {message_handlers} message, {callback_handlers} callback handlers")

    await db.close()


asyncio.run(debug_routers())