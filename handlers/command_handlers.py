# handlers/command_handlers.py
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from services.user_service import user_service
from services.chat_service import chat_service
from keyboards.main_keyboards import main_menu_kb, chat_mode_kb, searching_kb
from core.bot import bot  # Для отправки сообщений партнеру

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    # Регистрируем пользователя и показываем основное меню
    await user_service.register_user(
        message.from_user.id,
        message.from_user.username or f"id_{message.from_user.id}"
    )

    await message.answer(
        "👋 Добро пожаловать в анонимный чат! Нажмите 'Начать поиск', чтобы найти собеседника.",
        reply_markup=main_menu_kb
    )


@router.message(Command("newchat"))
@router.message(lambda message: message.text == "🔎 Начать поиск собеседника")
async def cmd_newchat(message: Message):
    user_id = message.from_user.id

    # Сначала проверяем, не находится ли он уже в чате/поиске
    current_status = await user_service.get_user_status(user_id)
    if current_status in ('searching', 'chatting'):
        await message.answer("Вы уже в поиске или чате.")
        return

    # Начинаем поиск
    partner_id = await chat_service.start_searching(user_id)

    if partner_id:
        # Найдена пара!
        await message.answer("✅ Собеседник найден! Можете начать общение.", reply_markup=chat_mode_kb)
        await bot.send_message(partner_id, "✅ Собеседник найден! Можете начать общение.", reply_markup=chat_mode_kb)
    else:
        # Поиск продолжается
        await message.answer("⏳ Идет поиск собеседника. Вы можете отменить поиск.", reply_markup=searching_kb)


@router.message(Command("stop"))
@router.message(lambda message: message.text == "❌ Остановить чат")
async def cmd_stop_chat(message: Message):
    user_id = message.from_user.id
    current_status = await user_service.get_user_status(user_id)

    if current_status == 'chatting':
        partner_id = await chat_service.end_chat(user_id)

        # Уведомляем текущего пользователя
        await message.answer("💔 Чат завершен.", reply_markup=main_menu_kb)

        # Уведомляем партнера
        if partner_id:
            await bot.send_message(partner_id, "💔 Собеседник завершил чат.", reply_markup=main_menu_kb)

    elif current_status == 'searching':
        # Если в поиске, то отменяем поиск
        partner_id = await chat_service.end_chat(user_id)  # end_chat сбрасывает статус в 'menu'
        await message.answer("❌ Поиск отменен.", reply_markup=main_menu_kb)

    else:
        await message.answer("Вы не находитесь в активном чате или поиске.", reply_markup=main_menu_kb)