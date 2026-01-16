from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
import logging

from .service import broadcast_service
from .keyboards import *
from .states import BroadcastStates
from .utils import safe_edit_message

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """Команда для админов"""
    logger.info(f"🎯 /broadcast от пользователя {message.from_user.id}")

    if not await broadcast_service.is_admin(message.from_user.id):
        await message.answer("❌ Нет прав доступа")
        return

    # Получаем статистику пользователей
    available_users = await broadcast_service.get_available_users_count()

    await message.answer(
        f"📢 <b>Панель управления рассылками</b>\n\n"
        f"👥 Доступно пользователей: {available_users}\n\n"
        "Выберите действие:",
        reply_markup=broadcast_main_kb
    )


@router.callback_query(F.data == "broadcast_create")
async def broadcast_create(callback: CallbackQuery, state: FSMContext):
    """Создание новой рассылки"""
    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        "📝 <b>Создание рассылки</b>\n\n"
        "Выберите тип рассылки:",
        broadcast_filters_kb
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_all")
async def broadcast_all_users(callback: CallbackQuery, state: FSMContext):
    """Рассылка всем пользователям"""
    available_users = await broadcast_service.get_available_users_count()

    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        f"👥 <b>Рассылка всем пользователям</b>\n\n"
        f"👥 Будет отправлено: {available_users} пользователям\n\n"
        "Отправьте сообщение для рассылки (текст, фото или видео):",
        None
    )
    await state.update_data(filters={})
    await state.set_state(BroadcastStates.waiting_message)
    await callback.answer()


@router.callback_query(F.data == "broadcast_test")
async def broadcast_test(callback: CallbackQuery, state: FSMContext):
    """Тестовая рассылка"""
    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        "🧪 <b>Тестовая рассылка</b>\n\n"
        "Отправьте сообщение для тестовой рассылки (10 пользователей):",
        None
    )
    await state.update_data(filters={"limit": 10})
    await state.set_state(BroadcastStates.waiting_message)
    await callback.answer()


@router.callback_query(F.data == "broadcast_users")
async def broadcast_users(callback: CallbackQuery):
    """Показывает список пользователей"""
    from core.database import db

    users = await db.execute("SELECT user_id, username, first_name FROM users")
    available_count = 0

    text = "👥 <b>Пользователи в базе:</b>\n\n"

    for user in users[:10]:  # Показываем первые 10
        user_id = user['user_id']
        username = user['username'] or 'нет'
        first_name = user['first_name'] or 'Не указано'

        # Проверяем доступность
        try:
            await callback.bot.send_chat_action(user_id, "typing")
            status = "✅"
            available_count += 1
        except:
            status = "❌"

        text += f"{status} {user_id} - {first_name} (@{username})\n"

    text += f"\n📊 <b>Итого:</b> {available_count}/{len(users)} доступных пользователей"

    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        text,
        broadcast_main_kb
    )
    await callback.answer()


@router.message(BroadcastStates.waiting_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обработка сообщения для рассылки"""
    try:
        data = await state.get_data()
        filters = data.get('filters', {})

        # Получаем пользователей по фильтрам
        user_ids = await broadcast_service.get_users_for_broadcast(filters)
        total_users = len(user_ids)

        if total_users == 0:
            await message.answer("❌ Нет пользователей по выбранным фильтрам")
            await state.clear()
            return

        # Сохраняем сообщение для рассылки
        await state.update_data(
            message_text=message.text or message.caption,
            message_type='text' if message.text else 'photo' if message.photo else 'video',
            file_id=message.photo[-1].file_id if message.photo else message.video.file_id if message.video else None
        )

        # Показываем подтверждение
        await message.answer(
            f"🎯 <b>Подтверждение рассылки</b>\n\n"
            f"👥 Получателей: {total_users} пользователей\n"
            f"📝 Тип: {'Текст' if message.text else 'Фото' if message.photo else 'Видео'}\n\n"
            f"<b>Предпросмотр:</b>\n"
            f"{message.text or message.caption or '📎 Медиа-сообщение'}\n\n"
            f"Запустить рассылку?",
            reply_markup=confirm_broadcast_kb
        )

    except Exception as e:
        logger.error(f"❌ Ошибка подготовки рассылки: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}")
        await state.clear()


@router.callback_query(F.data == "broadcast_confirm")
async def broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и запуск рассылки"""
    try:
        data = await state.get_data()
        filters = data.get('filters', {})
        message_text = data.get('message_text')
        message_type = data.get('message_type')
        file_id = data.get('file_id')

        # СОЗДАЕМ РАССЫЛКУ В БАЗЕ ДАННЫХ
        broadcast_id = await broadcast_service.create_broadcast(
            admin_id=callback.from_user.id,
            message_text=message_text,
            message_type=message_type,
            file_id=file_id,
            filters=filters
        )

        if not broadcast_id:
            await callback.message.edit_text("❌ Ошибка создания рассылки")
            await state.clear()
            await callback.answer()
            return

        # Получаем пользователей
        user_ids = await broadcast_service.get_users_for_broadcast(filters)
        total_users = len(user_ids)

        await callback.message.edit_text(f"🔄 Начинаю рассылку #{broadcast_id} для {total_users} пользователей...")

        # ЗАПУСКАЕМ РАССЫЛКУ
        await broadcast_service.start_broadcast(broadcast_id, callback.bot)

        # Формируем отчет
        stats = await broadcast_service.get_broadcast_stats(broadcast_id)

        if stats:
            success_count = stats['sent_count']
            failed_count = stats['total_users'] - success_count if stats['total_users'] else 0
        else:
            success_count = 0
            failed_count = total_users

        report_text = (
            f"✅ <b>Рассылка #{broadcast_id} завершена!</b>\n\n"
            f"📊 Статистика:\n"
            f"• ✅ Успешно: {success_count}\n"
            f"• ❌ Ошибок: {failed_count}\n"
            f"• 📈 Успех: {(success_count / total_users * 100):.1f}%"
        )

        await callback.message.edit_text(report_text)

    except Exception as e:
        logger.error(f"❌ Ошибка рассылки: {e}")
        await callback.message.edit_text(f"❌ Ошибка: {str(e)}")

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    await state.clear()
    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        "❌ Рассылка отменена",
        None
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_back")
async def broadcast_back(callback: CallbackQuery, state: FSMContext):
    """Назад в главное меню рассылок"""
    await state.clear()
    await safe_edit_message(  # 👈 ИСПОЛЬЗУЙ safe_edit_message
        callback,
        "📢 <b>Панель управления рассылками</b>\n\n"
        "Выберите действие:",
        broadcast_main_kb
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_list")
async def broadcast_list(callback: CallbackQuery):
    """Показывает список рассылок админа"""
    user_id = callback.from_user.id

    if not await broadcast_service.is_admin(user_id):
        await callback.answer("❌ Нет прав доступа")
        return

    try:
        # Получаем рассылки админа
        broadcasts = await broadcast_service.get_admin_broadcasts(user_id)

        if not broadcasts:
            await safe_edit_message(
                callback,
                "📝 <b>Мои рассылки</b>\n\n"
                "У вас пока нет созданных рассылок.",
                None
            )
            await callback.answer()
            return

        text = "📝 <b>Мои рассылки</b>\n\n"

        for broadcast in broadcasts[:5]:  # Показываем последние 5
            status_emoji = {
                'draft': '📝',
                'sending': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(broadcast['status'], '❓')

            # ИСПРАВЛЕНИЕ: правильно форматируем дату
            created_at = broadcast['created_at']
            if hasattr(created_at, 'strftime'):
                # Если это datetime объект
                created_date = created_at.strftime('%d.%m.%Y')
            else:
                # Если это строка
                created_date = str(created_at)[:10]

            text += f"{status_emoji} Рассылка #{broadcast['broadcast_id']}\n"
            text += f"   📊 Статус: {broadcast['status']}\n"
            text += f"   👥 Отправлено: {broadcast['sent_count']}/{broadcast['total_users'] or 0}\n"
            text += f"   📅 Создана: {created_date}\n\n"

        await safe_edit_message(callback, text, get_broadcast_list_kb(broadcasts))

    except Exception as e:
        logger.error(f"❌ Ошибка получения списка рассылок: {e}")
        await safe_edit_message(
            callback,
            "❌ Ошибка при получении списка рассылок",
            None
        )

    await callback.answer()


@router.callback_query(F.data == "broadcast_stats")
async def broadcast_stats(callback: CallbackQuery):
    """Показывает статистику рассылок"""
    user_id = callback.from_user.id

    if not await broadcast_service.is_admin(user_id):
        await callback.answer("❌ Нет прав доступа")
        return

    try:
        # Получаем все рассылки админа для статистики
        broadcasts = await broadcast_service.get_admin_broadcasts(user_id, limit=20)

        total_broadcasts = len(broadcasts)
        completed = sum(1 for b in broadcasts if b['status'] == 'completed')
        sending = sum(1 for b in broadcasts if b['status'] == 'sending')
        draft = sum(1 for b in broadcasts if b['status'] == 'draft')
        cancelled = sum(1 for b in broadcasts if b['status'] == 'cancelled')

        total_sent = sum(b.get('sent_count', 0) for b in broadcasts)
        total_users = sum(b.get('total_users', 0) for b in broadcasts)

        if total_users > 0:
            success_rate = (total_sent / total_users) * 100
        else:
            success_rate = 0

        text = (
            "📈 <b>Статистика рассылок</b>\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• 📝 Всего рассылок: {total_broadcasts}\n"
            f"• ✅ Завершено: {completed}\n"
            f"• 🔄 В процессе: {sending}\n"
            f"• 📋 Черновики: {draft}\n"
            f"• ❌ Отменено: {cancelled}\n\n"
            f"📨 <b>Доставка:</b>\n"
            f"• 👥 Всего получателей: {total_users}\n"
            f"• ✅ Успешно отправлено: {total_sent}\n"
            f"• 📈 Успешность: {success_rate:.1f}%\n\n"
            f"<i>Статистика за последние 20 рассылок</i>"
        )

        await safe_edit_message(callback, text, broadcast_main_kb)

    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        await safe_edit_message(
            callback,
            "❌ Ошибка при получении статистики",
            None
        )

    await callback.answer()


@router.callback_query(F.data.startswith("broadcast_view_"))
async def broadcast_view(callback: CallbackQuery):
    """Показывает детали конкретной рассылки"""
    user_id = callback.from_user.id

    if not await broadcast_service.is_admin(user_id):
        await callback.answer("❌ Нет прав доступа")
        return

    try:
        broadcast_id = int(callback.data.replace("broadcast_view_", ""))

        # Получаем детальную статистику рассылки
        stats = await broadcast_service.get_broadcast_stats(broadcast_id)

        if not stats:
            await safe_edit_message(
                callback,
                "❌ Рассылка не найдена",
                None
            )
            await callback.answer()
            return

        # Форматируем статус
        status_texts = {
            'draft': '📝 Черновик',
            'sending': '🔄 Отправляется',
            'completed': '✅ Завершена',
            'cancelled': '❌ Отменена'
        }

        status = status_texts.get(stats['status'], stats['status'])

        # ИСПРАВЛЕНИЕ: правильно форматируем даты
        def format_date(date_value):
            if not date_value:
                return 'Не отправлена'
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d.%m.%Y %H:%M')
            return str(date_value)[:16]

        created_at = format_date(stats['created_at'])
        sent_at = format_date(stats['sent_at'])

        text = (
            f"📋 <b>Детали рассылки #{stats['broadcast_id']}</b>\n\n"
            f"📊 <b>Статус:</b> {status}\n"
            f"📅 <b>Создана:</b> {created_at}\n"
            f"🕒 <b>Отправлена:</b> {sent_at}\n\n"
            f"📨 <b>Статистика доставки:</b>\n"
            f"• ✅ Успешно: {stats.get('sent_count', 0)}\n"
            f"• 👥 Всего получателей: {stats.get('total_users', 0)}\n"
            f"• 📈 Успешность: {stats.get('success_rate', 0):.1f}%\n\n"
            f"💬 <b>Сообщение:</b>\n"
            f"{stats['message_text'][:100]}..."
        )

        await safe_edit_message(callback, text, broadcast_main_kb)

    except Exception as e:
        logger.error(f"❌ Ошибка просмотра рассылки: {e}")
        await safe_edit_message(
            callback,
            "❌ Ошибка при просмотре рассылки",
            None
        )

    await callback.answer()


@router.callback_query(F.data == "broadcast_filters")
async def broadcast_filters(callback: CallbackQuery, state: FSMContext):
    """Настройка фильтров для рассылки"""
    await safe_edit_message(
        callback,
        "🎯 <b>Настройка фильтров</b>\n\n"
        "Выберите параметры для фильтрации пользователей:",
        filters_setup_kb
    )
    await callback.answer()


@router.callback_query(F.data == "filter_gender")
async def filter_gender(callback: CallbackQuery, state: FSMContext):
    """Выбор пола для фильтра"""
    await safe_edit_message(
        callback,
        "👤 <b>Фильтр по полу</b>\n\n"
        "Выберите пол пользователей для рассылки:",
        filter_gender_kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("filter_gender_"))
async def set_gender_filter(callback: CallbackQuery, state: FSMContext):
    """Установка фильтра по полу"""
    gender_map = {
        "filter_gender_male": "male",
        "filter_gender_female": "female",
        "filter_gender_any": "any"
    }

    gender_key = callback.data
    gender_value = gender_map.get(gender_key, "any")

    # Сохраняем фильтр в состоянии
    data = await state.get_data()
    filters = data.get('filters', {})
    filters['gender'] = gender_value

    await state.update_data(filters=filters)

    # Показываем подтверждение
    gender_texts = {
        "male": "👨 Мужской",
        "female": "👩 Женский",
        "any": "👥 Любой"
    }

    await safe_edit_message(
        callback,
        f"✅ <b>Фильтр по полу установлен:</b> {gender_texts[gender_value]}\n\n"
        "Продолжайте настройку фильтров или нажмите '✅ Готово':",
        filters_setup_kb
    )
    await callback.answer()


@router.callback_query(F.data == "filters_done")
async def filters_done(callback: CallbackQuery, state: FSMContext):
    """Завершение настройки фильтров"""
    data = await state.get_data()
    filters = data.get('filters', {})

    # Получаем количество пользователей по фильтрам
    available_users = await broadcast_service.get_users_count_by_filters(filters)

    # Формируем текст с информацией о фильтрах
    filter_info = "📋 <b>Установленные фильтры:</b>\n"

    if filters.get('gender'):
        gender_texts = {
            "male": "👨 Мужской",
            "female": "👩 Женский",
            "any": "👥 Любой"
        }
        filter_info += f"• Пол: {gender_texts.get(filters['gender'], 'Любой')}\n"
    else:
        filter_info += "• Пол: 👥 Любой\n"

    filter_info += f"\n👥 <b>Будет отправлено:</b> {available_users} пользователям\n\n"
    filter_info += "Отправьте сообщение для рассылки (текст, фото или видео):"

    await safe_edit_message(
        callback,
        filter_info,
        None
    )
    await state.set_state(BroadcastStates.waiting_message)
    await callback.answer()


@router.callback_query(F.data == "filter_age")
async def filter_age(callback: CallbackQuery, state: FSMContext):
    """Настройка фильтра по возрасту (заглушка)"""
    await callback.answer("ℹ️ Фильтр по возрасту будет добавлен в будущих обновлениях", show_alert=True)


@router.callback_query(F.data == "filter_activity")
async def filter_activity(callback: CallbackQuery, state: FSMContext):
    """Настройка фильтра по активности (заглушка)"""
    await callback.answer("ℹ️ Фильтр по активности будет добавлен в будущих обновлениях", show_alert=True)