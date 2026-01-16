from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from broadcasts.keyboards import broadcast_main_kb  # 👈 ИСПРАВЛЕННЫЙ ИМПОРТ

# Главное меню админки
admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Дашборд"), KeyboardButton(text="👥 Пользователи")],
        [KeyboardButton(text="⚠️ Жалобы"), KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🔧 Система")],
        [KeyboardButton(text="⬅️ Выйти из админки")]
    ],
    resize_keyboard=True
)

# Инлайн кнопки для дашборда
dashboard_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh")],
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📈 Графики", callback_data="admin_charts")
        ],
        [InlineKeyboardButton(text="📋 Экспорт данных", callback_data="admin_export")]
    ]
)

# Кнопки управления пользователями
users_management_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin_find_user")],
        [InlineKeyboardButton(text="📉 Проблемные", callback_data="admin_problem_users")],
        [InlineKeyboardButton(text="🏆 Топ", callback_data="admin_top_users")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_users_stats")]
    ]
)

# Кнопки для действий с пользователем
user_actions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Забанить", callback_data="admin_ban_user")],
        [InlineKeyboardButton(text="✉️ Написать", callback_data="admin_message_user")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_user_stats")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_to_users")]
    ]
)

# Кнопки системного меню
system_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Перезапустить бота", callback_data="admin_restart")],
        [InlineKeyboardButton(text="🧹 Очистка кэша", callback_data="admin_clear_cache")],
        [InlineKeyboardButton(text="📦 Бэкап БД", callback_data="admin_backup")],
        [InlineKeyboardButton(text="📊 Метрики", callback_data="admin_metrics")]
    ]
)

# Импорт клавиатуры рассылок
from broadcasts.keyboards import broadcast_main_kb