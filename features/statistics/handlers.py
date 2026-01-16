from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import logging

from .service import stats_service
from keyboards import main_menu_kb

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Показывает статистику пользователя"""
    user_id = message.from_user.id
    stats = await stats_service.get_user_stats(user_id)

    if stats:
        stats_text = (
            f"<b>📊 Ваша статистика:</b>\n\n"
            f"💬 Всего чатов: {stats['total_chats']}\n"
            f"✅ Завершено чатов: {stats['completed_chats']}\n"
            f"✉️ Отправлено сообщений: {stats['message_count']}\n"
            f"⭐ Текущий рейтинг: {stats['rating']:.1f}/10\n"
            f"📈 Успешность: {stats['success_rate']:.1f}%\n"
            f"⏱️ Средняя продолжительность чата: {stats['avg_chat_duration']}\n"
            f"📅 Дата регистрации: {stats['created_at']}"
        )
        await message.answer(stats_text)
    else:
        await message.answer(
            "❌ Статистика не найдена. Используйте /start для регистрации."
        )


@router.message(Command("global_stats"))
async def cmd_global_stats(message: Message):
    """Показывает глобальную статистику бота (только для админов)"""
    # Простая проверка на админа (замените на вашу логику)
    if message.from_user.id != 2043400004:  # Ваш ID
        await message.answer("❌ Эта команда только для администраторов")
        return

    stats = await stats_service.get_global_stats()

    if stats:
        stats_text = (
            f"<b>🌐 Глобальная статистика бота:</b>\n\n"
            f"👥 Всего пользователей: {stats['total_users']}\n"
            f"💬 Всего чатов: {stats['total_chats']}\n"
            f"✉️ Всего сообщений: {stats['total_messages']}\n"
            f"🔥 Активных за 24ч: {stats['active_users_24h']}"
        )
        await message.answer(stats_text)
    else:
        await message.answer("❌ Ошибка получения глобальной статистики")


@router.callback_query(F.data == "my_stats")
async def my_stats_callback(callback: CallbackQuery):
    """Показывает статистику через callback"""
    user_id = callback.from_user.id
    stats = await stats_service.get_user_stats(user_id)

    if stats:
        stats_text = (
            f"<b>📊 Ваша статистика:</b>\n\n"
            f"💬 Всего чатов: {stats['total_chats']}\n"
            f"✅ Завершено чатов: {stats['completed_chats']}\n"
            f"✉️ Отправлено сообщений: {stats['message_count']}\n"
            f"⭐ Текущий рейтинг: {stats['rating']:.1f}/10\n"
            f"📈 Успешность: {stats['success_rate']:.1f}%\n"
            f"⏱️ Средняя продолжительность чата: {stats['avg_chat_duration']}\n"
            f"📅 Дата регистрации: {stats['created_at']}"
        )
        await callback.message.edit_text(stats_text)
    else:
        await callback.message.edit_text("❌ Статистика не найдена")

    await callback.answer()
stats_router = router
