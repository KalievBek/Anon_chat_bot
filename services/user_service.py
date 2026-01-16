import logging
from core.database import db

logger = logging.getLogger(__name__)


class UserService:
    async def register_user(self, user_id: int, username: str, first_name: str = ""):
        """Регистрирует или обновляет данные пользователя"""
        try:
            user = await db.execute("SELECT * FROM users WHERE user_id = $1", user_id)
            if not user:
                await db.execute_commit("""
                    INSERT INTO users (user_id, username, first_name, status, rating) 
                    VALUES ($1, $2, $3, $4, $5)
                """, user_id, username, first_name, 'menu', 10.0)  # Начальный рейтинг 10
                logger.info(f"✅ Зарегистрирован новый пользователь: {user_id}")
            else:
                await db.execute_commit("""
                    UPDATE users SET username = $1, first_name = $2 WHERE user_id = $3
                """, username, first_name, user_id)
                logger.info(f"✅ Обновлен пользователь: {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации пользователя {user_id}: {e}")

    async def get_user_profile(self, user_id: int) -> dict:
        """Получает профиль пользователя"""
        try:
            rows = await db.execute("SELECT * FROM users WHERE user_id = $1", user_id)
            if rows:
                profile = dict(rows[0])
                return {
                    'user_id': profile['user_id'],
                    'username': profile['username'] or 'не указан',
                    'first_name': profile['first_name'] or 'не указано',
                    'gender': profile['gender'] or 'не указан',
                    'age': profile['age'] or 'не указан',
                    'interests': profile['interests'] or 'не указаны',
                    'rating': float(profile['rating']) if profile['rating'] else 10.0,
                    'total_chats': profile['total_chats'] or 0,
                    'created_at': str(profile['created_at'])[:10] if profile['created_at'] else 'неизвестно'
                }
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения профиля: {e}")
            return None

    async def get_user_stats(self, user_id: int) -> dict:
        """Получает статистику пользователя"""
        try:
            rows = await db.execute("""
                SELECT total_chats, rating, created_at 
                FROM users WHERE user_id = $1
            """, user_id)

            if rows:
                messages_rows = await db.execute("""
                    SELECT COUNT(*) as message_count FROM messages 
                    WHERE user_id = $1
                """, user_id)

                row = rows[0]
                return {
                    'total_chats': row['total_chats'] or 0,
                    'rating': float(row['rating']) if row['rating'] else 10.0,
                    'created_at': str(row['created_at'])[:10] if row['created_at'] else 'неизвестно',
                    'message_count': messages_rows[0]['message_count'] if messages_rows else 0
                }
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return None

    async def set_user_status(self, user_id: int, status: str):
        """Устанавливает статус пользователя"""
        await db.execute_commit("UPDATE users SET status = $1 WHERE user_id = $2", status, user_id)

    async def set_current_chat(self, user_id: int, partner_id: int):
        """Устанавливает текущий чат"""
        await db.execute_commit("UPDATE users SET current_chat_id = $1 WHERE user_id = $2", partner_id, user_id)

    async def get_current_chat(self, user_id: int) -> int | None:
        """Получает текущий чат"""
        rows = await db.execute("SELECT current_chat_id FROM users WHERE user_id = $1", user_id)
        return rows[0]['current_chat_id'] if rows and rows[0]['current_chat_id'] else None

    async def increment_chat_count(self, user_id: int):
        """Увеличивает счетчик чатов"""
        await db.execute_commit("UPDATE users SET total_chats = total_chats + 1 WHERE user_id = $1", user_id)

    async def update_rating(self, user_id: int, new_rating: float):
        """Обновляет рейтинг пользователя (среднее арифметическое)"""
        try:
            # Получаем текущий рейтинг и количество оценок
            current = await db.execute_scalar("SELECT rating FROM users WHERE user_id = $1", user_id)
            if current is None:
                current = 10.0

            # Простое обновление рейтинга (можно усложнить логику)
            await db.execute_commit("UPDATE users SET rating = $1 WHERE user_id = $2", new_rating, user_id)
            logger.info(f"✅ Рейтинг пользователя {user_id} обновлен: {new_rating}")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления рейтинга: {e}")

    async def get_partner_rating(self, user_id: int) -> float:
        """Получает рейтинг собеседника"""
        try:
            rating = await db.execute_scalar("SELECT rating FROM users WHERE user_id = $1", user_id)
            return float(rating) if rating else 10.0
        except Exception as e:
            logger.error(f"❌ Ошибка получения рейтинга: {e}")
            return 10.0

    async def update_profile(self, user_id: int, gender: str = None, age: int = None):
        """Обновляет профиль пользователя"""
        try:
            if gender:
                await db.execute_commit("UPDATE users SET gender = $1 WHERE user_id = $2", gender, user_id)
            if age:
                await db.execute_commit("UPDATE users SET age = $1 WHERE user_id = $2", age, user_id)
            logger.info(f"✅ Профиль пользователя {user_id} обновлен")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления профиля: {e}")


user_service = UserService()