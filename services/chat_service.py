# services/chat_service.py
from core.database import db
from .user_service import user_service


class ChatService:
    async def start_searching(self, user_id: int):
        """
        Ищет свободного собеседника или ставит пользователя в очередь.
        Возвращает ID партнера или None.
        """
        # 1. Ищем пользователя в статусе 'searching' (кроме самого себя)
        partner_row = await db.execute(
            "SELECT user_id FROM users WHERE status = 'searching' AND user_id != ? LIMIT 1",
            (user_id,)
        )

        if partner_row:
            partner_id = partner_row[0]['user_id']

            # 2. Нашли пару: меняем статус и связываем их
            await user_service.set_user_status(user_id, 'chatting')
            await user_service.set_current_chat(user_id, partner_id)

            await user_service.set_user_status(partner_id, 'chatting')
            await user_service.set_current_chat(partner_id, user_id)

            return partner_id
        else:
            # 3. Не нашли: ставим пользователя в очередь
            await user_service.set_user_status(user_id, 'searching')
            return None

    async def end_chat(self, user_id: int):
        """Завершает текущий чат для пользователя и его собеседника."""
        partner_id = await user_service.get_current_chat(user_id)

        # Сброс данных для текущего пользователя
        await user_service.set_user_status(user_id, 'menu')
        await user_service.set_current_chat(user_id, None)

        # Сброс данных для партнера
        if partner_id:
            await user_service.set_user_status(partner_id, 'menu')
            await user_service.set_current_chat(partner_id, None)

        return partner_id


chat_service = ChatService()