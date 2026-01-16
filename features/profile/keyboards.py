from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Основное меню профиля
profile_main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить пол", callback_data="edit_gender")],
        [InlineKeyboardButton(text="🎂 Изменить возраст", callback_data="edit_age")],
        [InlineKeyboardButton(text="🎯 Изменить интересы", callback_data="edit_interests")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
)

# Клавиатура для выбора пола
edit_gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="set_gender_male")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="set_gender_female")],
        [InlineKeyboardButton(text="❓ Не указывать", callback_data="set_gender_unspecified")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]
    ]
)

# Клавиатура для выбора возрастной группы
edit_age_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👶 13-17 лет", callback_data="set_age_15")],
        [InlineKeyboardButton(text="👨 18-25 лет", callback_data="set_age_20")],
        [InlineKeyboardButton(text="🧔 26-35 лет", callback_data="set_age_30")],
        [InlineKeyboardButton(text="👴 36+ лет", callback_data="set_age_40")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]
    ]
)

# Клавиатура для выбора интересов
edit_interests_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 Игры", callback_data="interest_games"),
            InlineKeyboardButton(text="🎵 Музыка", callback_data="interest_music")
        ],
        [
            InlineKeyboardButton(text="🎬 Фильмы", callback_data="interest_movies"),
            InlineKeyboardButton(text="📚 Книги", callback_data="interest_books")
        ],
        [
            InlineKeyboardButton(text="⚽ Спорт", callback_data="interest_sports"),
            InlineKeyboardButton(text="💻 IT", callback_data="interest_it")
        ],
        [
            InlineKeyboardButton(text="🍳 Кулинария", callback_data="interest_cooking"),
            InlineKeyboardButton(text="✈️ Путешествия", callback_data="interest_travel")
        ],
        [InlineKeyboardButton(text="✅ Готово", callback_data="interests_done")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]
    ]
)