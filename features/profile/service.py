import logging
from core.database import db

logger = logging.getLogger(__name__)


class ProfileService:
    async def get_user_profile(self, user_id: int) -> dict:
        """Получает полный профиль пользователя"""
        try:
            row = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            if row:
                profile = dict(row[0])

                # Форматируем данные для отображения
                return {
                    'user_id': profile['user_id'],
                    'username': profile['username'] or 'не указан',
                    'first_name': profile['first_name'] or 'не указано',
                    'gender': profile['gender'] or 'не указан',
                    'age': profile['age'] or 'не указан',
                    'interests': profile['interests'] or 'не указаны',
                    'rating': profile['rating'] or 5.0,
                    'total_chats': profile['total_chats'] or 0,
                    'created_at': profile['created_at'][:10] if profile['created_at'] else 'неизвестно'
                }
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения профиля: {e}")
            return None

    async def update_profile(self, user_id: int, **kwargs):
        """Обновляет данные профиля"""
        try:
            if not kwargs:
                return False

            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(user_id)

            query = f"UPDATE users SET {set_clause} WHERE user_id = ?"
            await db.execute_commit(query, tuple(values))
            logger.info(f"✅ Профиль пользователя {user_id} обновлен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка обновления профиля: {e}")
            return False


# Глобальный экземпляр
profile_service = ProfileService()