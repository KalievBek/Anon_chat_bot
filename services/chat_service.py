# services/chat_service.py
import random
from core.database import db
from services.user_service import user_service


class ChatService:
    @staticmethod
    async def start_searching(user_id: int):
        """Начинает поиск собеседника для пользователя"""
        try:
            # Устанавливаем статус поиска
            await user_service.update_user_status(user_id, 'searching')

            # Ищем случайного собеседника
            partner = await user_service.find_user_by_status('searching')

            if partner and partner['user_id'] != user_id:
                # Создаем чат между пользователями
                partner_id = partner['user_id']

                # Создаем запись о чате
                await db.execute_commit(
                    """INSERT INTO active_chats (user1_id, user2_id) 
                       VALUES (?, ?)""",
                    (min(user_id, partner_id), max(user_id, partner_id))
                )

                # Получаем ID созданного чата
                result = await db.execute(
                    "SELECT chat_id FROM active_chats WHERE user1_id = ? AND user2_id = ?",
                    (min(user_id, partner_id), max(user_id, partner_id))
                )

                chat_id = result[0]['chat_id'] if result else None

                if chat_id:
                    # Обновляем статусы и устанавливаем чат
                    await user_service.update_user_status(user_id, 'chatting')
                    await user_service.update_user_status(partner_id, 'chatting')
                    await user_service.set_current_chat(user_id, chat_id)
                    await user_service.set_current_chat(partner_id, chat_id)

                    return partner_id

            return None

        except Exception as e:
            print(f"❌ Error starting search: {e}")
            await user_service.update_user_status(user_id, 'menu')
            return None

    @staticmethod
    async def end_chat(user_id: int):
        """Завершает чат для пользователя"""
        try:
            # Получаем информацию о текущем чате
            current_chat_id = await user_service.get_current_chat(user_id)

            if not current_chat_id:
                return None

            # Находим собеседника
            result = await db.execute(
                "SELECT user1_id, user2_id FROM active_chats WHERE chat_id = ?",
                (current_chat_id,)
            )

            if not result:
                return None

            chat_info = result[0]
            companion_id = chat_info['user1_id'] if chat_info['user1_id'] != user_id else chat_info['user2_id']

            # Обновляем статусы пользователей
            await user_service.update_user_status(user_id, 'menu')
            await user_service.set_current_chat(user_id, None)

            # Помечаем чат как неактивный
            await db.execute_commit(
                "UPDATE active_chats SET is_active = FALSE WHERE chat_id = ?",
                (current_chat_id,)
            )

            return companion_id

        except Exception as e:
            print(f"❌ Error ending chat: {e}")
            await user_service.update_user_status(user_id, 'menu')
            await user_service.set_current_chat(user_id, None)
            return None

    @staticmethod
    async def get_companion_id(user_id: int):
        """Получает ID собеседника пользователя"""
        try:
            current_chat_id = await user_service.get_current_chat(user_id)

            if not current_chat_id:
                return None

            result = await db.execute(
                "SELECT user1_id, user2_id FROM active_chats WHERE chat_id = ? AND is_active = TRUE",
                (current_chat_id,)
            )

            if not result:
                return None

            chat_info = result[0]
            return chat_info['user1_id'] if chat_info['user1_id'] != user_id else chat_info['user2_id']

        except Exception as e:
            print(f"❌ Error getting companion: {e}")
            return None


chat_service = ChatService()