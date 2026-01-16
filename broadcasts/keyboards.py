from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню рассылок
broadcast_main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="broadcast_create")],
        [InlineKeyboardButton(text="📊 Мои рассылки", callback_data="broadcast_list")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="broadcast_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="broadcast_users")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ]
)

# Фильтры для рассылки
broadcast_filters_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всем пользователям", callback_data="broadcast_all")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast_back")]
    ]
)

# Фильтры настроек
filters_setup_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👤 Пол", callback_data="filter_gender")],
        [InlineKeyboardButton(text="🎂 Возраст", callback_data="filter_age")],
        [InlineKeyboardButton(text="💬 Активность", callback_data="filter_activity")],
        [InlineKeyboardButton(text="✅ Готово", callback_data="filters_done")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast_create")]
    ]
)

# Выбор пола для фильтра
filter_gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="filter_gender_male")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="filter_gender_female")],
        [InlineKeyboardButton(text="👥 Любой", callback_data="filter_gender_any")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast_filters")]
    ]
)

# Подтверждение рассылки
confirm_broadcast_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Запустить", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="broadcast_cancel")
        ]
    ]
)

def get_broadcast_list_kb(broadcasts):
    """Клавиатура списка рассылок"""
    keyboard = []
    for broadcast in broadcasts[:5]:  # Показываем последние 5
        status_emoji = {
            'draft': '📝',
            'sending': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }.get(broadcast['status'], '❓')

        text = f"{status_emoji} Рассылка #{broadcast['broadcast_id']}"
        keyboard.append([InlineKeyboardButton(text=text,
                                              callback_data=f"broadcast_view_{broadcast['broadcast_id']}")])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)