# keyboards/main_keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Главное меню"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти собеседника")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📋 Правила")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

def get_chat_mode_menu():
    """Меню в режиме чата"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭️ Следующий"), KeyboardButton(text="🚫 Завершить диалог")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

def get_searching_keyboard():
    """Клавиатура во время поиска"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Остановить поиск")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

def get_profile_keyboard():
    """Клавиатура профиля"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти собеседника")],
            [KeyboardButton(text="📋 Правила"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )