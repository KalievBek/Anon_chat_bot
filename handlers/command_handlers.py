# handlers/command_handlers.py
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.user_service import user_service
from services.chat_service import chat_service
from keyboards.main_keyboards import get_main_menu, get_chat_mode_menu, get_searching_keyboard, get_profile_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or f"id_{message.from_user.id}"

    # Регистрируем пользователя
    await user_service.register_user(user_id, username)

    welcome_text = """
👋 *Добро пожаловать в Анонимный Чат!*

Здесь вы можете:
• 🔍 Найти случайного собеседника
• 💬 Общаться анонимно  
• ⏭️ Переключаться между собеседниками
• 👤 Настроить свой профиль

*Начните общение - нажмите "🔍 Найти собеседника"!*
"""
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Обработчик команды /profile"""
    user_id = message.from_user.id
    try:
        current_status = await user_service.get_user_status(user_id)
        companion_id = await user_service.get_current_chat(user_id)

        profile_text = f"""
👤 *Ваш профиль:*

🆔 ID: `{user_id}`
👤 Имя: {message.from_user.full_name}
📛 Username: @{message.from_user.username or 'не указан'}
📊 Статус: {current_status}
💬 Собеседник: {f'ID {companion_id}' if companion_id else 'нет'}

*Настройте свой профиль для лучшего подбора собеседников!*
"""
        await message.answer(profile_text, reply_markup=get_profile_keyboard(), parse_mode='Markdown')
    except Exception as e:
        await message.answer("❌ Ошибка при загрузке профиля", reply_markup=get_main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Обработчик команды /help"""
    help_text = """
ℹ️ *Помощь по боту:*

*Основные команды:*
/start - начать работу с ботом
/profile - просмотреть свой профиль  
/help - показать эту справку

*Кнопки управления:*
🔍 *Найти собеседника* - начать поиск
⏭️ *Следующий* - найти нового собеседника
🚫 *Завершить диалог* - закончить чат
👤 *Профиль* - управление профилем
📋 *Правила* - правила общения

💡 *Совет:* Будьте вежливы и уважительны!
"""
    await message.answer(help_text, reply_markup=get_main_menu(), parse_mode='Markdown')


@router.message(Command("rules"))
async def cmd_rules(message: Message, state: FSMContext):
    """Обработчик команды /rules"""
    rules_text = """
📋 *Правила общения в чатах:*

1. ✅ Уважайте собеседников
2. ✅ Запрещен спам и реклама
3. ✅ Не раскрывайте личную информацию
4. ✅ Сообщения должны быть уместными
5. ✅ Запрещены оскорбления и дискриминация
6. ✅ Не передавайте контакты и ссылки

⚠️ *Нарушители будут заблокированы!*

🙏 *Соблюдайте правила для комфортного общения!*
"""
    await message.answer(rules_text, reply_markup=get_main_menu(), parse_mode='Markdown')


@router.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext):
    """Обработчик команды /stop - завершить чат"""
    user_id = message.from_user.id
    try:
        companion_id = await chat_service.end_chat(user_id)

        if companion_id:
            await message.bot.send_message(companion_id, "❌ *Собеседник завершил диалог*", parse_mode='Markdown')

        await message.answer("💬 *Диалог завершен!*", parse_mode='Markdown', reply_markup=get_main_menu())
    except Exception as e:
        await message.answer("❌ Ошибка при завершении чата", reply_markup=get_main_menu())


@router.message(Command("next"))
async def cmd_next(message: Message, state: FSMContext):
    """Обработчик команды /next - следующий собеседник"""
    user_id = message.from_user.id
    try:
        # Сначала завершаем текущий чат
        companion_id = await chat_service.end_chat(user_id)

        if companion_id:
            await message.bot.send_message(companion_id, "🔁 *Собеседник перешел к следующему...*",
                                           parse_mode='Markdown')

        # Начинаем новый поиск
        partner_id = await chat_service.start_searching(user_id)

        if partner_id:
            await message.answer("✅ *Новый собеседник найден!*", parse_mode='Markdown',
                                 reply_markup=get_chat_mode_menu())
        else:
            await message.answer("⏭️ *Ищем следующего собеседника...*", parse_mode='Markdown',
                                 reply_markup=get_searching_keyboard())
    except Exception as e:
        await message.answer("❌ Ошибка при поиске следующего собеседника", reply_markup=get_main_menu())