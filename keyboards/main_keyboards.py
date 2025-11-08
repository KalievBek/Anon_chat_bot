# keyboards/main_keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (Reply Keyboard)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Найти собеседника")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📋 Правила")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Режим чата (Reply Keyboard)
chat_mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭️ Следующий"), KeyboardButton(text="🚫 Завершить диалог")],
        [KeyboardButton(text="👤 Профиль")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Режим поиска (Inline Keyboard)
searching_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить поиск", callback_data="cancel_search")],
    ]
)

# Клавиатура для профиля
profile_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ]
)

def get_main_menu():
    return main_menu_kb

def get_chat_mode_menu():
    return chat_mode_kb

def get_searching_keyboard():
    return searching_kb

def get_profile_keyboard():
    return profile_kb