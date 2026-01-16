import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import dp, bot, db
from handlers import commands_router, messages_router, callbacks_router
from admin import admin_router
from broadcasts import broadcast_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("🚀 Запуск бота...")

        # Настраиваем базу данных ПЕРВЫМ ДЕЛОМ
        await db.setup()
        logger.info("✅ База данных настроена")

        # ✅ ПРАВИЛЬНЫЙ ПОРЯДОК РОУТЕРОВ:
        dp.include_router(broadcast_router)    # 👈 ПЕРВАЯ - важные команды
        dp.include_router(admin_router)        # 👈 ВТОРАЯ
        dp.include_router(commands_router)     # 👈 ТРЕТЬЯ
        dp.include_router(messages_router)     # 👈 ЧЕТВЕРТАЯ
        dp.include_router(callbacks_router)    # 👈 ПЯТАЯ

        print("✅ Роутеры зарегистрированы:")
        print(f"  - broadcast_router: {len(broadcast_router.message.handlers)} message, {len(broadcast_router.callback_query.handlers)} callback")
        print(f"  - admin_router: {len(admin_router.message.handlers)} message, {len(admin_router.callback_query.handlers)} callback")
        print(f"  - commands_router: {len(commands_router.message.handlers)} message, {len(commands_router.callback_query.handlers)} callback")
        print(f"  - messages_router: {len(messages_router.message.handlers)} message, {len(messages_router.callback_query.handlers)} callback")
        print(f"  - callbacks_router: {len(callbacks_router.message.handlers)} message, {len(callbacks_router.callback_query.handlers)} callback")

        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Бот запущен!")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())