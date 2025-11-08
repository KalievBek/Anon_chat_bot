# services/user_service.py
from core.database import db

class UserService:
    @staticmethod
    async def register_user(user_id: int, username: str = ""):
        """Регистрирует или обновляет пользователя"""
        try:
            full_name = f"{username or f'user_{user_id}'}"
            await db.execute_commit(
                """INSERT OR REPLACE INTO users 
                   (user_id, username, full_name, status) 
                   VALUES (?, ?, ?, 'menu')""",
                (user_id, username, full_name)
            )
            return True
        except Exception as e:
            print(f"❌ Error registering user: {e}")
            return False

    @staticmethod
    async def get_user(user_id: int):
        """Получает информацию о пользователе"""
        try:
            result = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None

    @staticmethod
    async def get_user_status(user_id: int):
        """Получает статус пользователя"""
        try:
            result = await db.execute(
                "SELECT status FROM users WHERE user_id = ?",
                (user_id,)
            )
            return result[0]['status'] if result else 'menu'
        except Exception as e:
            print(f"❌ Error getting user status: {e}")
            return 'menu'

    @staticmethod
    async def update_user_status(user_id: int, status: str):
        """Обновляет статус пользователя"""
        try:
            await db.execute_commit(
                "UPDATE users SET status = ? WHERE user_id = ?",
                (status, user_id)
            )
            return True
        except Exception as e:
            print(f"❌ Error updating user status: {e}")
            return False

    @staticmethod
    async def set_current_chat(user_id: int, chat_id: int):
        """Устанавливает текущий чат для пользователя"""
        try:
            await db.execute_commit(
                "UPDATE users SET current_chat_id = ? WHERE user_id = ?",
                (chat_id, user_id)
            )
            return True
        except Exception as e:
            print(f"❌ Error setting current chat: {e}")
            return False

    @staticmethod
    async def get_current_chat(user_id: int):
        """Получает ID текущего чата пользователя"""
        try:
            result = await db.execute(
                "SELECT current_chat_id FROM users WHERE user_id = ?",
                (user_id,)
            )
            return result[0]['current_chat_id'] if result and result[0]['current_chat_id'] else None
        except Exception as e:
            print(f"❌ Error getting current chat: {e}")
            return None

    @staticmethod
    async def find_user_by_status(status: str):
        """Находит пользователя по статусу"""
        try:
            result = await db.execute(
                "SELECT * FROM users WHERE status = ? LIMIT 1",
                (status,)
            )
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Error finding user by status: {e}")
            return None

user_service = UserService()