from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

# Главное меню
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Найти собеседника"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚙️ Настройки поиска")],
        [KeyboardButton(text="📋 Правила"), KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Меню чата
chat_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭️ Следующий собеседник"), KeyboardButton(text="🚫 Завершить чат")],
        [KeyboardButton(text="🎲 Отправить действие"), KeyboardButton(text="⭐ Оценить собеседника")],
        [KeyboardButton(text="⬅️ В главное меню")]
    ],
    resize_keyboard=True
)

# Меню поиска
search_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отменить поиск")],
        [KeyboardButton(text="⬅️ В главное меню")]
    ],
    resize_keyboard=True
)

# Инлайн кнопки для поиска
searching_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить поиск", callback_data="cancel_search")],
        [InlineKeyboardButton(text="⚙️ Изменить настройки", callback_data="change_search_settings")]
    ]
)

# Клавиатура для рейтинга
rating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1⭐", callback_data="rate_1"),
            InlineKeyboardButton(text="2⭐", callback_data="rate_2"),
            InlineKeyboardButton(text="3⭐", callback_data="rate_3"),
            InlineKeyboardButton(text="4⭐", callback_data="rate_4"),
            InlineKeyboardButton(text="5⭐", callback_data="rate_5")
        ],
        [
            InlineKeyboardButton(text="6⭐", callback_data="rate_6"),
            InlineKeyboardButton(text="7⭐", callback_data="rate_7"),
            InlineKeyboardButton(text="8⭐", callback_data="rate_8"),
            InlineKeyboardButton(text="9⭐", callback_data="rate_9"),
            InlineKeyboardButton(text="10⭐", callback_data="rate_10")
        ],
        [InlineKeyboardButton(text="🚫 Пропустить", callback_data="rate_skip")]
    ]
)

# Кнопки действий в чате
chat_actions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data="action_like"),
            InlineKeyboardButton(text="👎", callback_data="action_dislike"),
            InlineKeyboardButton(text="❤️", callback_data="action_heart")
        ],
        [
            InlineKeyboardButton(text="😊", callback_data="action_smile"),
            InlineKeyboardButton(text="😂", callback_data="action_laugh"),
            InlineKeyboardButton(text="😢", callback_data="action_cry")
        ],
        [
            InlineKeyboardButton(text="🎮", callback_data="action_game"),
            InlineKeyboardButton(text="📷", callback_data="action_photo"),
            InlineKeyboardButton(text="🎵", callback_data="action_music")
        ]
    ]
)

# Настройки поиска (упрощенные)
settings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👥 Пол собеседника", callback_data="setting_gender")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="edit_my_profile")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
)

# Выбор пола для поиска
gender_preference_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨 Только мужчины", callback_data="pref_male")],
        [InlineKeyboardButton(text="👩 Только женщины", callback_data="pref_female")],
        [InlineKeyboardButton(text="👥 Любой пол", callback_data="pref_any")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings")]
    ]
)

# Выбор пола для профиля
profile_gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="profile_gender_male")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="profile_gender_female")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]
    ]
)

# Профиль пользователя
profile_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить пол", callback_data="edit_profile_gender")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
)

def get_main_menu():
    return main_menu_kb

def get_chat_menu():
    return chat_menu_kb

def get_search_menu():
    return search_menu_kb

def get_rating_kb():
    return rating_kb