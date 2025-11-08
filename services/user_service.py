# services/user_service.py
from core.database import db


class UserService:
    async def register_user(self, user_id: int, username: str):
        """Регистрирует пользователя, если он еще не зарегистрирован."""
        user = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not user:
            await db.execute_commit(
                "INSERT INTO users (user_id, username, status) VALUES (?, ?, ?)",
                (user_id, username, 'menu')
            )

    async def get_user_status(self, user_id: int) -> str:
        """Получает текущий статус пользователя."""
        row = await db.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
        return row[0]['status'] if row else 'not_found'

    async def set_user_status(self, user_id: int, status: str):
        """Устанавливает новый статус пользователя."""
        await db.execute_commit("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))

    async def set_current_chat(self, user_id: int, partner_id: int):
        """Устанавливает ID собеседника."""
        await db.execute_commit("UPDATE users SET current_chat_id = ? WHERE user_id = ?", (partner_id, user_id))

    async def get_current_chat(self, user_id: int) -> int | None:
        """Получает ID текущего собеседника."""
        row = await db.execute("SELECT current_chat_id FROM users WHERE user_id = ?", (user_id,))
        # Важно: SQLITE возвращает NULL как None в Python
        return row[0]['current_chat_id'] if row and row[0]['current_chat_id'] else None


user_service = UserService()