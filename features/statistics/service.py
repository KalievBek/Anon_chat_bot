import logging
from core.database import db

logger = logging.getLogger(__name__)


class StatisticsService:
    async def get_user_stats(self, user_id: int) -> dict:
        """Получает статистику пользователя"""
        try:
            # Получаем базовую информацию
            user_row = await db.execute("""
                SELECT total_chats, rating, created_at 
                FROM users WHERE user_id = ?
            """, (user_id,))

            if not user_row:
                return None

            user_data = dict(user_row[0])

            # Получаем количество сообщений
            messages_row = await db.execute("""
                SELECT COUNT(*) as message_count FROM messages 
                WHERE user_id = ?
            """, (user_id,))

            # Получаем количество завершенных чатов
            completed_chats_row = await db.execute("""
                SELECT COUNT(*) as completed_chats FROM chats 
                WHERE (user1_id = ? OR user2_id = ?) AND ended_at IS NOT NULL
            """, (user_id, user_id))

            # Получаем среднюю продолжительность чатов
            avg_duration_row = await db.execute("""
                SELECT AVG(JULIANDAY(ended_at) - JULIANDAY(started_at)) as avg_duration
                FROM chats 
                WHERE (user1_id = ? OR user2_id = ?) AND ended_at IS NOT NULL
            """, (user_id, user_id))

            message_count = messages_row[0]['message_count'] if messages_row else 0
            completed_chats = completed_chats_row[0]['completed_chats'] if completed_chats_row else 0
            avg_duration = avg_duration_row[0]['avg_duration'] if avg_duration_row and avg_duration_row[0][
                'avg_duration'] else 0

            # Форматируем среднюю продолжительность
            if avg_duration > 0:
                hours = int(avg_duration * 24)
                minutes = int((avg_duration * 24 * 60) % 60)
                avg_duration_text = f"{hours}ч {minutes}м"
            else:
                avg_duration_text = "неизвестно"

            return {
                'total_chats': user_data['total_chats'] or 0,
                'completed_chats': completed_chats,
                'message_count': message_count,
                'rating': user_data['rating'] or 5.0,
                'avg_chat_duration': avg_duration_text,
                'created_at': user_data['created_at'][:10] if user_data['created_at'] else 'неизвестно',
                'success_rate': (completed_chats / user_data['total_chats'] * 100) if user_data[
                                                                                          'total_chats'] > 0 else 0
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return None

    async def get_global_stats(self) -> dict:
        """Получает глобальную статистику бота"""
        try:
            # Общее количество пользователей
            total_users_row = await db.execute("SELECT COUNT(*) as count FROM users")
            # Общее количество чатов
            total_chats_row = await db.execute("SELECT COUNT(*) as count FROM chats")
            # Общее количество сообщений
            total_messages_row = await db.execute("SELECT COUNT(*) as count FROM messages")
            # Активные пользователи за последние 24 часа
            active_users_row = await db.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE datetime(created_at) > datetime('now', '-1 day')
            """)

            return {
                'total_users': total_users_row[0]['count'] if total_users_row else 0,
                'total_chats': total_chats_row[0]['count'] if total_chats_row else 0,
                'total_messages': total_messages_row[0]['count'] if total_messages_row else 0,
                'active_users_24h': active_users_row[0]['count'] if active_users_row else 0
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения глобальной статистики: {e}")
            return None


# Глобальный экземпляр
stats_service = StatisticsService()