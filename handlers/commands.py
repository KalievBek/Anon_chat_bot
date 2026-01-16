from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import asyncio
import logging

from keyboards import (
    main_menu_kb, chat_menu_kb, search_menu_kb,
    searching_inline_kb, rating_kb, profile_kb, settings_kb
)

# Импортируем сервисы
from services.user_service import user_service
from services.chat_service import chat_service
from services.search_service import search_service
from core.database import db

router = Router()
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения состояния
active_chats = {}
searching_users = []
search_tasks = {}
awaiting_rating = {}  # Пользователи, которые должны оценить собеседника


async def check_registration(user_id: int) -> bool:
    """Проверяет зарегистрирован ли пользователь"""
    profile = await user_service.get_user_profile(user_id)
    return profile is not None


@router.message(CommandStart())
async def cmd_start(message: Message):
    # РЕГИСТРИРУЕМ ПОЛЬЗОВАТЕЛЯ ПРИ СТАРТЕ
    await user_service.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or ""
    )

    await message.answer(
        "👋 Привет! Это анонимный чат.\n\n"
        "✨ <b>Возможности:</b>\n"
        "• 🔍 Поиск случайных собеседников\n"
        "• 💬 Анонимное общение\n"
        "• ⭐ Система рейтингов\n"
        "• 📊 Статистика и профиль\n\n"
        "Выберите действие в меню ниже 👇",
        reply_markup=main_menu_kb
    )


@router.message(F.text == "🔍 Найти собеседника")
async def cmd_search(message: Message):
    user_id = message.from_user.id

    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(user_id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    if user_id in active_chats:
        await message.answer("❌ Вы уже в активном чате!", reply_markup=chat_menu_kb)
        return

    if user_id in searching_users:
        await message.answer("⏳ Поиск уже запущен...", reply_markup=search_menu_kb)
        return

    # Добавляем в поиск
    searching_users.append(user_id)

    # ЗАПУСКАЕМ ПОИСК ЧЕРЕЗ SearchService
    search_result = await search_service.start_search(user_id)

    if search_result['success'] and search_result['partner_id']:
        # Нашли собеседника сразу
        partner_id = search_result['partner_id']
        await connect_users(user_id, partner_id, message.bot)
    else:
        # Показываем сообщение о поиске
        await message.answer(
            "🔍 <b>Ищем собеседника...</b>\n\n"
            "⏳ Ожидайте подбора подходящей пары\n"
            f"🎯 Фильтр: {await get_current_preference_text(user_id)}\n"
            "✨ Вы можете отменить поиск кнопкой ниже",
            reply_markup=searching_inline_kb
        )
        # Запускаем фоновый поиск
        task = asyncio.create_task(background_search(user_id, message.bot))
        search_tasks[user_id] = task


async def get_current_preference_text(user_id: int) -> str:
    """Получает текст текущих предпочтений"""
    try:
        result = await db.execute("SELECT gender_preference FROM search_queue WHERE user_id = $1", user_id)
        if result:
            preference = result[0]['gender_preference']
            preference_texts = {
                "male": "👨 Только мужчины",
                "female": "👩 Только женщины",
                "any": "👥 Любой пол"
            }
            return preference_texts.get(preference, "👥 Любой пол")
    except:
        pass
    return "👥 Любой пол"


async def background_search(user_id: int, bot_instance):
    """Фоновый поиск собеседника"""
    try:
        # Ждем до 60 секунд
        for i in range(30):
            await asyncio.sleep(2)

            if user_id not in searching_users:
                return

            # Получаем текущие предпочтения пользователя
            result = await db.execute("SELECT gender_preference FROM search_queue WHERE user_id = $1", user_id)
            if not result:
                break

            gender_preference = result[0]['gender_preference']

            # Ищем собеседника через SearchService
            partner_id = await search_service._find_compatible_partner(user_id, gender_preference)

            if partner_id:
                await connect_users(user_id, partner_id, bot_instance)
                return

        # Если не нашли за 60 секунд
        if user_id in searching_users:
            searching_users.remove(user_id)
            await search_service.cancel_search(user_id)
            await bot_instance.send_message(
                user_id,
                "❌ Не удалось найти подходящего собеседника. Попробуйте позже!",
                reply_markup=main_menu_kb
            )

    except Exception as e:
        logger.error(f"❌ Ошибка фонового поиска: {e}")
        if user_id in searching_users:
            searching_users.remove(user_id)
            await search_service.cancel_search(user_id)


async def connect_users(user_id: int, partner_id: int, bot_instance):
    """Соединяет двух пользователей в чате"""
    # Создаем чат в базе данных
    chat_id = await chat_service._create_chat(user_id, partner_id)
    if chat_id:
        await chat_service._pair_users(user_id, partner_id, chat_id)

    # Добавляем в активные чаты
    active_chats[user_id] = partner_id
    active_chats[partner_id] = user_id

    # Убираем из поиска
    if user_id in searching_users:
        searching_users.remove(user_id)
    if partner_id in searching_users:
        searching_users.remove(partner_id)

    # Получаем рейтинги
    user_rating = await user_service.get_partner_rating(user_id)
    partner_rating = await user_service.get_partner_rating(partner_id)

    # Уведомляем обоих
    try:
        await bot_instance.send_message(
            user_id,
            f"✅ <b>Собеседник найден!</b>\n\n"
            f"⭐ Рейтинг собеседника: <b>{partner_rating:.1f}/10</b>\n"
            f"💬 Можете начинать общение\n"
            f"🎲 Используйте кнопки для действий\n"
            f"⭐ Чтобы оценить - нажмите 'Оценить собеседника'",
            reply_markup=chat_menu_kb
        )
        await bot_instance.send_message(
            partner_id,
            f"✅ <b>Собеседник найден!</b>\n\n"
            f"⭐ Рейтинг собеседника: <b>{user_rating:.1f}/10</b>\n"
            f"💬 Можете начинать общение\n"
            f"🎲 Используйте кнопки для действий\n"
            f"⭐ Чтобы оценить - нажмите 'Оценить собеседника'",
            reply_markup=chat_menu_kb
        )
    except:
        if user_id in active_chats:
            del active_chats[user_id]
        if partner_id in active_chats:
            del active_chats[partner_id]


@router.message(F.text == "👤 Мой профиль")
async def cmd_profile(message: Message):
    """Профиль пользователя"""
    user_id = message.from_user.id

    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(user_id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    profile = await user_service.get_user_profile(user_id)

    if profile:
        gender_text = {
            'male': '👨 Мужской',
            'female': '👩 Женский',
            'not_specified': '❓ Не указан'
        }.get(profile.get('gender'), '❓ Не указан')

        profile_text = (
            f"<b>👤 Ваш профиль:</b>\n\n"
            f"👤 Имя: {profile.get('first_name', 'Не указано')}\n"
            f"📛 Username: @{profile.get('username', 'нет')}\n"
            f"🚻 Пол: {gender_text}\n"
            f"💬 Чатов: {profile.get('total_chats', 0)}\n"
            f"⭐ Рейтинг: {profile.get('rating', 10.0):.1f}/10"
        )
        await message.answer(profile_text, reply_markup=profile_kb)
    else:
        await message.answer("❌ Профиль не найден. Используйте /start")


@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    """Простая статистика"""
    user_id = message.from_user.id

    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(user_id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    stats = await user_service.get_user_stats(user_id)

    if stats:
        stats_text = (
            f"<b>📊 Ваша статистика:</b>\n\n"
            f"💬 Всего чатов: {stats['total_chats']}\n"
            f"✉️ Сообщений: {stats['message_count']}\n"
            f"⭐ Рейтинг: {stats['rating']:.1f}/10\n"
            f"📅 Регистрация: {stats['created_at'][:10]}"
        )
        await message.answer(stats_text)
    else:
        await message.answer("❌ Статистика не найдена. Используйте /start")


@router.message(F.text == "⭐ Оценить собеседника")
async def cmd_rate_partner(message: Message):
    """Ручная оценка собеседника"""
    user_id = message.from_user.id

    if user_id not in active_chats:
        await message.answer("❌ У вас нет активного чата")
        return

    partner_id = active_chats[user_id]
    partner_rating = await user_service.get_partner_rating(partner_id)

    await message.answer(
        f"⭐ <b>Оцените собеседника</b>\n\n"
        f"Текущий рейтинг собеседника: <b>{partner_rating:.1f}/10</b>\n"
        f"Как вы оцениваете общение?",
        reply_markup=rating_kb
    )
    awaiting_rating[user_id] = partner_id


@router.message(F.text == "⏭️ Следующий собеседник")
async def cmd_next(message: Message):
    user_id = message.from_user.id

    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(user_id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    # Завершаем текущий чат если есть
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        # ЗАВЕРШАЕМ ЧАТ В БАЗЕ ДАННЫХ
        await chat_service.end_chat(user_id)
        del active_chats[user_id]
        del active_chats[partner_id]

        # Просим оценить собеседника ОБОИХ пользователей
        await ask_for_rating(user_id, partner_id, message.bot)
        await ask_for_rating(partner_id, user_id, message.bot)

        try:
            await message.bot.send_message(partner_id, "🔁 Собеседник перешел к следующему...",
                                           reply_markup=main_menu_kb)
        except:
            pass

    # Начинаем новый поиск
    await cmd_search(message)


@router.message(F.text == "🚫 Завершить чат")
async def cmd_stop_chat(message: Message):
    user_id = message.from_user.id

    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(user_id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        # ЗАВЕРШАЕМ ЧАТ В БАЗЕ ДАННЫХ
        await chat_service.end_chat(user_id)
        del active_chats[user_id]
        del active_chats[partner_id]

        # Просим оценить собеседника ОБОИХ пользователей
        await ask_for_rating(user_id, partner_id, message.bot)
        await ask_for_rating(partner_id, user_id, message.bot)

        await message.answer("💔 Чат завершен", reply_markup=main_menu_kb)
        try:
            await message.bot.send_message(partner_id, "💔 Собеседник завершил чат", reply_markup=main_menu_kb)
        except:
            pass
    else:
        await message.answer("❌ Вы не в активном чате", reply_markup=main_menu_kb)


@router.message(F.text == "🎲 Отправить действие")
async def cmd_send_action(message: Message):
    """Отправка действия в чате"""
    from keyboards import chat_actions_kb

    if message.from_user.id not in active_chats:
        await message.answer("❌ У вас нет активного чата")
        return

    await message.answer(
        "🎲 <b>Выберите действие:</b>",
        reply_markup=chat_actions_kb
    )


@router.message(F.text == "⚙️ Настройки поиска")
async def cmd_settings(message: Message):
    """Настройки поиска"""
    # 🔒 ПРОВЕРКА РЕГИСТРАЦИИ
    if not await check_registration(message.from_user.id):
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        return

    await message.answer(
        "<b>⚙️ Настройки поиска</b>\n\n"
        "Настройте параметры поиска собеседников:",
        reply_markup=settings_kb
    )


@router.message(F.text == "📋 Правила")
async def cmd_rules(message: Message):
    rules_text = (
        "<b>📋 Правила анонимного чата:</b>\n\n"
        "✅ <b>Разрешено:</b>\n"
        "• Уважительное общение\n"
        "• Обмен мнениями\n"
        "• Поиск друзей по интересам\n\n"
        "❌ <b>Запрещено:</b>\n"
        "• Оскорбления и угрозы\n"
        "• Спам и реклама\n"
        "• Распространение личных данных\n"
        "• Контент 18+ без согласия\n\n"
        "⚠️ <b>Нарушение правил</b> ведет к бану!"
    )
    await message.answer(rules_text)


@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    help_text = (
        "<b>ℹ️ Помощь по боту:</b>\n\n"
        "<b>Основные команды:</b>\n"
        "🔍 <b>Найти собеседника</b> - начать поиск\n"
        "👤 <b>Мой профиль</b> - настройки профиля\n"
        "📊 <b>Статистика</b> - ваша активность\n"
        "⚙️ <b>Настройки поиска</b> - фильтры поиска\n\n"
        "<b>В чате:</b>\n"
        "⏭️ <b>Следующий</b> - найти нового собеседника\n"
        "🚫 <b>Завершить</b> - выйти из чата\n"
        "🎲 <b>Действия</b> - отправить стикер/действие\n"
        "⭐ <b>Оценить</b> - поставить оценку собеседнику"
    )
    await message.answer(help_text)


@router.message(F.text == "⬅️ В главное меню")
async def cmd_back_to_main(message: Message):
    user_id = message.from_user.id

    # Отменяем поиск если был
    if user_id in searching_users:
        searching_users.remove(user_id)
    if user_id in search_tasks:
        search_tasks[user_id].cancel()
        del search_tasks[user_id]

    await message.answer("📋 Главное меню", reply_markup=main_menu_kb)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await cmd_back_to_main(message)


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    user_id = message.from_user.id
    await message.answer(
        f"🆔 <b>Ваш User ID:</b> <code>{user_id}</code>\n\n"
        f"📛 <b>Имя:</b> {message.from_user.first_name or 'не указано'}\n"
        f"👤 <b>Username:</b> @{message.from_user.username or 'нет'}"
    )


async def ask_for_rating(user_id: int, partner_id: int, bot):
    """Просит пользователя оценить собеседника"""
    try:
        partner_rating = await user_service.get_partner_rating(partner_id)
        await bot.send_message(
            user_id,
            f"⭐ <b>Оцените собеседника</b>\n\n"
            f"Текущий рейтинг собеседника: <b>{partner_rating:.1f}/10</b>\n"
            f"Как вы оцениваете общение?",
            reply_markup=rating_kb
        )
        awaiting_rating[user_id] = partner_id
    except Exception as e:
        logger.error(f"❌ Ошибка запроса рейтинга: {e}")