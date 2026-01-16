from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import logging

from .service import profile_service
from .keyboards import profile_main_kb, edit_gender_kb, edit_age_kb, edit_interests_kb

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "👤 Мой профиль")
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Показывает профиль пользователя"""
    user_id = message.from_user.id
    profile = await profile_service.get_user_profile(user_id)

    if profile:
        gender_emoji = {
            'male': '👨',
            'female': '👩',
            'not_specified': '❓'
        }.get(profile['gender'], '❓')

        profile_text = (
            f"<b>👤 Ваш профиль:</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👤 Имя: {profile['first_name']}\n"
            f"📛 Username: @{profile['username']}\n"
            f"{gender_emoji} Пол: {profile['gender']}\n"
            f"🎂 Возраст: {profile['age']}\n"
            f"🎯 Интересы: {profile['interests']}\n"
            f"⭐ Рейтинг: {profile['rating']:.1f}/10\n"
            f"💬 Чатов: {profile['total_chats']}\n"
            f"📅 Регистрация: {profile['created_at']}"
        )
        await message.answer(profile_text, reply_markup=profile_main_kb)
    else:
        await message.answer(
            "❌ Профиль не найден. Используйте /start для регистрации.",
            reply_markup=profile_main_kb
        )


@router.callback_query(F.data == "edit_gender")
async def edit_gender(callback: CallbackQuery):
    """Редактирование пола"""
    await callback.message.edit_text(
        "👤 <b>Выберите ваш пол:</b>",
        reply_markup=edit_gender_kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_gender_"))
async def set_gender(callback: CallbackQuery):
    """Установка пола"""
    gender_map = {
        "set_gender_male": "male",
        "set_gender_female": "female",
        "set_gender_unspecified": "not_specified"
    }

    gender = gender_map.get(callback.data, "not_specified")
    gender_text = {
        "male": "👨 Мужской",
        "female": "👩 Женский",
        "not_specified": "❓ Не указан"
    }.get(gender, "❓ Не указан")

    success = await profile_service.update_profile(callback.from_user.id, gender=gender)

    if success:
        await callback.message.edit_text(
            f"✅ Пол успешно изменен на: {gender_text}",
            reply_markup=profile_main_kb
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при изменении пола",
            reply_markup=profile_main_kb
        )
    await callback.answer()


@router.callback_query(F.data == "edit_age")
async def edit_age(callback: CallbackQuery):
    """Редактирование возраста"""
    await callback.message.edit_text(
        "🎂 <b>Выберите вашу возрастную группу:</b>",
        reply_markup=edit_age_kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_age_"))
async def set_age(callback: CallbackQuery):
    """Установка возраста"""
    age_map = {
        "set_age_15": 15,
        "set_age_20": 20,
        "set_age_30": 30,
        "set_age_40": 40
    }

    age = age_map.get(callback.data, 20)

    success = await profile_service.update_profile(callback.from_user.id, age=age)

    if success:
        await callback.message.edit_text(
            f"✅ Возраст успешно изменен на: {age} лет",
            reply_markup=profile_main_kb
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при изменении возраста",
            reply_markup=profile_main_kb
        )
    await callback.answer()


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    """Возврат к профилю"""
    user_id = callback.from_user.id
    profile = await profile_service.get_user_profile(user_id)

    if profile:
        gender_emoji = {
            'male': '👨',
            'female': '👩',
            'not_specified': '❓'
        }.get(profile['gender'], '❓')

        profile_text = (
            f"<b>👤 Ваш профиль:</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👤 Имя: {profile['first_name']}\n"
            f"📛 Username: @{profile['username']}\n"
            f"{gender_emoji} Пол: {profile['gender']}\n"
            f"🎂 Возраст: {profile['age']}\n"
            f"🎯 Интересы: {profile['interests']}\n"
            f"⭐ Рейтинг: {profile['rating']:.1f}/10\n"
            f"💬 Чатов: {profile['total_chats']}\n"
            f"📅 Регистрация: {profile['created_at']}"
        )
        await callback.message.edit_text(profile_text, reply_markup=profile_main_kb)
    await callback.answer()
profile_router = router
