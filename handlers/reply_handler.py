# handlers/reply_handler.py
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from services.chat_service import chat_service
from services.user_service import user_service
from keyboards.main_keyboards import get_main_menu, get_chat_mode_menu, get_searching_keyboard, get_profile_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "🔍 Найти собеседника")
async def search_from_reply(message: types.Message, state: FSMContext):
    """Поиск из reply-кнопки"""
    user_id = message.from_user.id

    try:
        # Проверяем статус пользователя
        current_status = await user_service.get_user_status(user_id)
        if current_status in ['chatting', 'searching']:
            await message.answer("❌ Вы уже в активном чате или поиске!", reply_markup=get_chat_mode_menu())
            return

        # Начинаем поиск
        partner_id = await chat_service.start_searching(user_id)

        if partner_id:
            await message.answer("✅ *Собеседник найден!* Можете начинать общение.",
                                 parse_mode='Markdown', reply_markup=get_chat_mode_menu())
            # Уведомляем собеседника
            await message.bot.send_message(partner_id, "✅ *Собеседник найден!* Можете начинать общение.",
                                           parse_mode='Markdown', reply_markup=get_chat_mode_menu())
        else:
            await message.answer("🔍 *Ищем собеседника...* Ожидайте.",
                                 parse_mode='Markdown', reply_markup=get_searching_keyboard())

    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer("❌ Ошибка при поиске собеседника", reply_markup=get_main_menu())


@router.message(F.text == "⏭️ Следующий")
async def next_from_reply(message: types.Message, state: FSMContext):
    """Следующий из reply-кнопки"""
    user_id = message.from_user.id

    try:
        # Завершаем текущий чат
        companion_id = await chat_service.end_chat(user_id)

        if companion_id:
            await message.bot.send_message(companion_id, "🔁 *Собеседник перешел к следующему...*",
                                           parse_mode='Markdown', reply_markup=get_main_menu())

        # Начинаем новый поиск
        partner_id = await chat_service.start_searching(user_id)

        if partner_id:
            await message.answer("✅ *Новый собеседник найден!*", parse_mode='Markdown',
                                 reply_markup=get_chat_mode_menu())
        else:
            await message.answer("⏭️ *Ищем следующего собеседника...*", parse_mode='Markdown',
                                 reply_markup=get_searching_keyboard())

    except Exception as e:
        logger.error(f"Next error: {e}")
        await message.answer("❌ Ошибка при поиске следующего собеседника", reply_markup=get_main_menu())


@router.message(F.text.in_(["🚫 Завершить диалог", "❌ Остановить чат"]))
async def stop_from_reply(message: types.Message, state: FSMContext):
    """Стоп из reply-кнопки"""
    user_id = message.from_user.id

    try:
        companion_id = await chat_service.end_chat(user_id)

        if companion_id:
            await message.bot.send_message(companion_id, "❌ *Собеседник завершил диалог*",
                                           parse_mode='Markdown', reply_markup=get_main_menu())

        await message.answer("💬 *Диалог завершен!*", parse_mode='Markdown', reply_markup=get_main_menu())

    except Exception as e:
        logger.error(f"Stop error: {e}")
        await message.answer("❌ Ошибка при завершении чата", reply_markup=get_main_menu())


@router.message(F.text == "👤 Профиль")
async def profile_from_reply(message: types.Message, state: FSMContext):
    """Профиль из reply-кнопки"""
    user_id = message.from_user.id

    try:
        current_status = await user_service.get_user_status(user_id)
        companion_id = await user_service.get_current_chat(user_id)

        # Экранируем специальные символы Markdown
        username = message.from_user.username or 'не указан'
        full_name = message.from_user.full_name or 'Не указано'

        # Экранирование символов Markdown
        def escape_markdown(text):
            if not text:
                return text
            escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in escape_chars:
                text = text.replace(char, f'\\{char}')
            return text

        username = escape_markdown(username)
        full_name = escape_markdown(full_name)
        current_status = escape_markdown(current_status)

        profile_text = f"""
👤 *Ваш профиль:*

🆔 ID: `{user_id}`
👤 Имя: {full_name}
📛 Username: @{username}
📊 Статус: {current_status}

*Настройте свой профиль для лучшего подбора собеседников\!*
"""
        await message.answer(profile_text, reply_markup=get_profile_keyboard(), parse_mode='MarkdownV2')

    except Exception as e:
        logger.error(f"Profile error: {e}")
        # Простой профиль без Markdown
        simple_profile = f"""
👤 Ваш профиль:

🆔 ID: {user_id}
👤 Имя: {message.from_user.full_name or 'Не указано'}
📛 Username: @{message.from_user.username or 'не указан'}

Функции профиля временно недоступны. Мы работаем над исправлением!
"""
        await message.answer(simple_profile, reply_markup=get_main_menu())


@router.message(F.text == "📋 Правила")
async def rules_from_reply(message: types.Message, state: FSMContext):
    """Правила из reply-кнопки"""
    rules_text = """
📋 *Правила общения в чатах:*

1\. ✅ Уважайте собеседников
2\. ✅ Запрещен спам и реклама
3\. ✅ Не раскрывайте личную информацию
4\. ✅ Сообщения должны быть уместными
5\. ✅ Запрещены оскорбления и дискриминация

⚠️ Нарушители будут заблокированы\!
"""
    await message.answer(rules_text, reply_markup=get_main_menu(), parse_mode='MarkdownV2')


@router.message(F.text == "ℹ️ Помощь")
async def help_from_reply(message: types.Message, state: FSMContext):
    """Помощь из reply-кнопки"""
    help_text = """
ℹ️ *Помощь по боту:*

🔍 *Найти собеседника* \- начать поиск случайного собеседника
⏭️ *Следующий* \- переключиться на нового собеседника  
🚫 *Завершить диалог* \- закончить текущий чат
👤 *Профиль* \- просмотреть и редактировать свой профиль
📋 *Правила* \- ознакомиться с правилами общения

💡 *Совет:* Будьте вежливы и уважительны к собеседникам\!
"""
    await message.answer(help_text, reply_markup=get_main_menu(), parse_mode='MarkdownV2')


@router.message(F.text == "🔎 Начать поиск собеседника")
async def start_search_from_reply(message: types.Message, state: FSMContext):
    """Альтернативная кнопка поиска"""
    await search_from_reply(message, state)