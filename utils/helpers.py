import logging

logger = logging.getLogger(__name__)


def format_user_profile(user_data: dict) -> str:
    """Форматирует профиль пользователя"""
    gender_map = {
        'male': '👨 Мужской',
        'female': '👩 Женский',
        'not_specified': '❓ Не указан'
    }

    return f"""
👤 <b>Ваш профиль:</b>

🆔 ID: <code>{user_data['user_id']}</code>
👤 Имя: {user_data['first_name'] or 'Не указано'}
📛 Username: @{user_data['username'] or 'нет'}
{gender_map.get(user_data['gender'], '❓')}
🎂 Возраст: {user_data['age'] or 'Не указан'}
🎯 Интересы: {user_data['interests'] or 'Не указаны'}
⭐ Рейтинг: {user_data['rating']:.1f}/10
💬 Чатов: {user_data['total_chats']}
    """.strip()


def format_user_stats(stats: dict) -> str:
    """Форматирует статистику пользователя"""
    return f"""
📊 <b>Ваша статистика:</b>

💬 Всего чатов: {stats['total_chats']}
✉️ Сообщений: {stats['messages_sent']}
⭐ Рейтинг: {stats['rating']:.1f}/10
📅 Регистрация: {stats['created_at'][:10]}
🕒 Активность: {stats['last_active'] or 'Недавно'}
    """.strip()