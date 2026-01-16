from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging

from keyboards import (
    main_menu_kb, settings_kb, gender_preference_kb,
    chat_actions_kb, profile_gender_kb, profile_kb, rating_kb
)
from services.user_service import user_service
from handlers.commands import awaiting_rating, searching_users, search_tasks, active_chats
from core.database import db

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "cancel_search")
async def cancel_search_callback(callback: CallbackQuery):
    """Отменяет поиск"""
    user_id = callback.from_user.id

    # 🔒 ПРОВЕРЯЕМ РЕГИСТРАЦИЮ
    profile = await user_service.get_user_profile(user_id)
    if not profile:
        await callback.message.edit_text("❌ Сначала зарегистрируйтесь через /start")
        await callback.answer()
        return

    if user_id in searching_users:
        searching_users.remove(user_id)
    if user_id in search_tasks:
        search_tasks[user_id].cancel()
        del search_tasks[user_id]

    await callback.message.edit_text("❌ Поиск отменен")
    await callback.message.answer("📋 Главное меню", reply_markup=main_menu_kb)
    await callback.answer()


@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery):
    """Обрабатывает оценку собеседника"""
    user_id = callback.from_user.id

    if user_id not in awaiting_rating:
        await callback.answer("❌ Оценка больше не актуальна")
        return

    partner_id = awaiting_rating[user_id]
    rating_action = callback.data.replace("rate_", "")

    if rating_action == "skip":
        await callback.message.edit_text("✅ Оценка пропущена")
        if user_id in awaiting_rating:
            del awaiting_rating[user_id]
        await callback.answer()
        return

    try:
        rating = int(rating_action)
        if 1 <= rating <= 10:
            # Обновляем рейтинг собеседника (среднее арифметическое)
            current_rating = await user_service.get_partner_rating(partner_id)
            new_rating = (current_rating + rating) / 2  # Простое среднее
            await user_service.update_rating(partner_id, new_rating)

            await callback.message.edit_text(
                f"✅ Вы оценили собеседника на <b>{rating}⭐</b>\n"
                f"Новый рейтинг собеседника: <b>{new_rating:.1f}/10</b>"
            )
            if user_id in awaiting_rating:
                del awaiting_rating[user_id]
        else:
            await callback.answer("❌ Неверная оценка")
    except ValueError:
        await callback.answer("❌ Ошибка оценки")

    await callback.answer()


@router.callback_query(F.data == "edit_my_profile")
async def edit_my_profile(callback: CallbackQuery):
    """Редактирование профиля"""
    await callback.message.edit_text(
        "👤 <b>Редактирование профиля</b>\n\n"
        "Выберите ваш пол:",
        reply_markup=profile_gender_kb
    )
    await callback.answer()


@router.callback_query(F.data == "edit_profile_gender")
async def edit_profile_gender(callback: CallbackQuery):
    """Изменение пола в профиле"""
    await callback.message.edit_text(
        "👤 <b>Изменение пола</b>\n\n"
        "Выберите ваш пол:",
        reply_markup=profile_gender_kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("profile_gender_"))
async def set_profile_gender(callback: CallbackQuery):
    """Установка пола в профиле"""
    gender = callback.data.replace("profile_gender_", "")

    gender_texts = {
        "male": "👨 Мужской",
        "female": "👩 Женский",
        "not_specified": "❓ Не указывать"
    }

    await user_service.update_profile(callback.from_user.id, gender=gender)

    await callback.message.edit_text(
        f"✅ Пол установлен: {gender_texts.get(gender, 'Не указан')}",
        reply_markup=profile_kb
    )
    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def show_my_stats(callback: CallbackQuery):
    """Показывает статистику пользователя"""
    from handlers.commands import cmd_stats
    await cmd_stats(callback.message)
    await callback.answer()


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    """Возврат к профилю"""
    from handlers.commands import cmd_profile
    await cmd_profile(callback.message)
    await callback.answer()


@router.callback_query(F.data == "change_search_settings")
async def change_search_settings(callback: CallbackQuery):
    """Изменение настроек поиска"""
    await callback.message.edit_text(
        "⚙️ <b>Настройки поиска</b>\n\n"
        "Выберите параметр для изменения:",
        reply_markup=settings_kb
    )
    await callback.answer()


@router.callback_query(F.data == "setting_gender")
async def setting_gender(callback: CallbackQuery):
    """Настройка пола собеседника"""
    await callback.message.edit_text(
        "👥 <b>Выберите пол собеседника:</b>",
        reply_markup=gender_preference_kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pref_"))
async def set_gender_preference(callback: CallbackQuery):
    """Установка предпочтений по полу"""
    preference = callback.data.replace("pref_", "")

    preference_texts = {
        "male": "👨 Только мужчины",
        "female": "👩 Только женщины",
        "any": "👥 Любой пол"
    }

    # Сохраняем предпочтения в базе
    user_id = callback.from_user.id
    await db.execute_commit("""
        INSERT INTO search_queue (user_id, gender_preference) 
        VALUES ($1, $2)
        ON CONFLICT (user_id) 
        DO UPDATE SET gender_preference = $2
    """, user_id, preference)

    await callback.message.edit_text(
        f"✅ Установлено: {preference_texts.get(preference, 'Любой пол')}\n\n"
        f"Теперь бот будет искать: {preference_texts.get(preference, 'Любой пол')}",
        reply_markup=settings_kb
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text("📋 Главное меню")
    await callback.message.answer("Выберите действие:", reply_markup=main_menu_kb)
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """Возврат к настройкам"""
    await callback.message.edit_text(
        "⚙️ <b>Настройки поиска</b>\n\n"
        "Выберите параметр для изменения:",
        reply_markup=settings_kb
    )
    await callback.answer()


# Обработчики действий в чате
@router.callback_query(F.data.startswith("action_"))
async def send_chat_action(callback: CallbackQuery):
    """Отправка действия в чате"""
    user_id = callback.from_user.id
    action = callback.data.replace("action_", "")

    action_texts = {
        "like": "👍",
        "dislike": "👎",
        "heart": "❤️",
        "smile": "😊",
        "laugh": "😂",
        "cry": "😢",
        "game": "🎮 предложил(а) сыграть в игру",
        "photo": "📷 предложил(а) обменяться фото",
        "music": "🎵 предложил(а) обменяться музыкой"
    }

    action_text = action_texts.get(action, "🎲")

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            await callback.bot.send_message(
                partner_id,
                f"🎲 Собеседник отправил: {action_text}"
            )
            await callback.answer("✅ Действие отправлено")
        except:
            await callback.answer("❌ Не удалось отправить действие")
    else:
        await callback.answer("❌ Нет активного чата")