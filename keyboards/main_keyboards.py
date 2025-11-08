# keyboards/main_keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (Reply Keyboard)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Начать поиск собеседника")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Режим чата (Reply Keyboard)
chat_mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Остановить чат")],
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