from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import logging
from broadcasts.keyboards import broadcast_main_kb
from broadcasts.service import broadcast_service  # 👈 ДОБАВЛЕН ИМПОРТ
from .admin_service import admin_service
from .admin_keyboards import (
    admin_main_kb, dashboard_kb, users_management_kb,
    user_actions_kb, system_kb
)
from core.database import db

router = Router()
# router.message.filter(IsAdminFilter())  # 👈 ВРЕМЕННО ОТКЛЮЧАЕМ
# router.callback_query.filter(IsAdminFilter())

logger = logging.getLogger(__name__)


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Главное меню админки"""
    user_id = message.from_user.id
    print(f"🔍 Попытка входа в админку: {user_id}")

    # ПРЯМАЯ ПРОВЕРКА - ЗАМЕНИ НА СВОЙ ID
    if user_id != 2043400004:  # 👈 ТВОЙ ID 2043400004
        await message.answer("❌ У вас нет доступа к админ-панели")
        return

    await message.answer(
        "🔧 <b>Панель администратора</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=admin_main_kb
    )


@router.message(F.text == "📊 Дашборд")
async def admin_dashboard(message: Message):
    """Дашборд с основной статистикой"""
    # ПРОВЕРКА ДОСТУПА
    if message.from_user.id != 2043400004:
        return

    stats = await admin_service.get_dashboard_stats()

    dashboard_text = f"""
📊 <b>LIVE ДАШБОРД АДМИНА</b>

👥 <b>ПОЛЬЗОВАТЕЛИ</b>
• Всего: {stats.total_users}
• Активных сегодня: {stats.active_today}
• В поиске: {stats.searches_now}

💬 <b>ЧАТЫ</b>
• Активных сейчас: {stats.active_chats_now}
• Сообщений сегодня: {stats.messages_today}

⭐ <b>РЕЙТИНГИ</b>
• Средний рейтинг: {stats.avg_rating}/10

⚠️ <b>МОДЕРАЦИЯ</b>
• Жалоб на рассмотрении: {stats.reports_pending}
    """

    await message.answer(dashboard_text, reply_markup=dashboard_kb)


@router.message(F.text == "👥 Пользователи")
async def admin_users(message: Message):
    """Управление пользователями"""
    if message.from_user.id != 2043400004:
        return

    await message.answer(
        "👥 <b>Управление пользователями</b>\n\n"
        "Выберите действие:",
        reply_markup=users_management_kb
    )


@router.message(F.text == "📢 Рассылка")
async def admin_broadcast(message: Message):
    """Обработчик кнопки Рассылка в админке"""
    user_id = message.from_user.id
    logger.info(f"🎯 Нажата кнопка '📢 Рассылка' пользователем {user_id}")

    if user_id != 2043400004:
        await message.answer("❌ Нет прав доступа")
        return

    # Используем broadcast_service для получения статистики
    available_users = await broadcast_service.get_available_users_count()

    await message.answer(
        f"📢 <b>Панель управления рассылками</b>\n\n"
        f"👥 Доступно пользователей: {available_users}\n\n"
        "Выберите действие:",
        reply_markup=broadcast_main_kb
    )


@router.message(F.text == "⚠️ Жалобы")
async def admin_reports(message: Message):
    """Жалобы пользователей"""
    if message.from_user.id != 2043400004:
        return
    # TODO: реализовать просмотр жалоб
    await message.answer("📋 <b>Система жалоб</b>\n\nРаздел в разработке...")


@router.message(F.text == "⚙️ Настройки")
async def admin_settings(message: Message):
    """Настройки бота"""
    if message.from_user.id != 2043400004:
        return
    await message.answer("⚙️ <b>Настройки бота</b>\n\nРаздел в разработке...")


@router.message(F.text == "🔧 Система")
async def admin_system(message: Message):
    """Системные утилиты"""
    if message.from_user.id != 2043400004:
        return

    metrics = await admin_service.get_system_metrics()

    system_text = f"""
🔧 <b>СИСТЕМНЫЕ МЕТРИКИ</b>

💾 <b>ПРОИЗВОДИТЕЛЬНОСТЬ</b>
• Подключения к БД: {metrics.db_connections}
• Память: {metrics.memory_usage}%
• Время ответа: {metrics.response_time}сек

⚠️ <b>ОШИБКИ</b>
• За последний час: {metrics.errors_last_hour}
    """

    await message.answer(system_text, reply_markup=system_kb)


@router.message(F.text == "⬅️ Выйти из админки")
async def admin_exit(message: Message):
    """Выход из админки"""
    from keyboards.main_keyboards import main_menu_kb
    await message.answer("✅ Вы вышли из панели администратора", reply_markup=main_menu_kb)


# Callback handlers
@router.callback_query(F.data == "admin_refresh")
async def refresh_dashboard(callback: CallbackQuery):
    """Обновление дашборда"""
    if callback.from_user.id != 2043400004:
        return
    await admin_dashboard(callback.message)
    await callback.answer("✅ Дашборд обновлен")


@router.callback_query(F.data == "admin_problem_users")
async def show_problem_users(callback: CallbackQuery):
    """Показывает проблемных пользователей"""
    if callback.from_user.id != 2043400004:
        return

    problem_users = await admin_service.get_problematic_users(5)

    if not problem_users:
        await callback.message.answer("✅ Проблемных пользователей не найдено")
        await callback.answer()
        return

    users_text = "📉 <b>ПРОБЛЕМНЫЕ ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for i, user in enumerate(problem_users, 1):
        users_text += f"{i}. ID: {user.user_id} | @{user.username}\n"
        users_text += f"   ⭐ Рейтинг: {user.rating} | Чатов: {user.total_chats}\n\n"

    await callback.message.answer(users_text)
    await callback.answer()


@router.callback_query(F.data == "admin_top_users")
async def show_top_users(callback: CallbackQuery):
    """Показывает топ пользователей"""
    if callback.from_user.id != 2043400004:
        return

    top_users = await admin_service.get_top_users(5)

    if not top_users:
        await callback.message.answer("❌ Топ пользователей не найден")
        await callback.answer()
        return

    users_text = "🏆 <b>ТОП ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for i, user in enumerate(top_users, 1):
        users_text += f"{i}. ID: {user.user_id} | @{user.username}\n"
        users_text += f"   ⭐ Рейтинг: {user.rating} | Чатов: {user.total_chats}\n\n"

    await callback.message.answer(users_text)
    await callback.answer()


@router.callback_query(F.data == "admin_metrics")
async def show_system_metrics(callback: CallbackQuery):
    """Подробные системные метрики"""
    if callback.from_user.id != 2043400004:
        return
    await admin_system(callback.message)
    await callback.answer()