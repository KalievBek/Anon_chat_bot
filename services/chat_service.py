import logging
import asyncio
from core.database import db
from services.user_service import user_service

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.active_searches = set()
        self.chat_pairs = {}

    async def start_searching(self, user_id: int, gender_preference: str = 'any') -> int | None:
        """Начинает поиск собеседника"""
        await db.execute_commit("""
            INSERT INTO search_queue (user_id, gender_preference) 
            VALUES ($1, $2)
            ON CONFLICT (user_id) 
            DO UPDATE SET gender_preference = $2, created_at = CURRENT_TIMESTAMP
        """, user_id, gender_preference)

        await user_service.set_user_status(user_id, 'searching')
        self.active_searches.add(user_id)

        partner_id = await self._find_companion(user_id, gender_preference)

        if partner_id:
            chat_id = await self._create_chat(user_id, partner_id)
            if chat_id:
                await self._pair_users(user_id, partner_id, chat_id)
                return partner_id

        return None

    async def _find_companion(self, user_id: int, gender_preference: str) -> int | None:
        """Ищет подходящего собеседника"""
        if gender_preference == 'any':
            query = """
                SELECT user_id FROM search_queue 
                WHERE user_id != $1 
                LIMIT 1
            """
            params = (user_id,)
        else:
            query = """
                SELECT sq.user_id FROM search_queue sq
                JOIN users u ON sq.user_id = u.user_id
                WHERE sq.user_id != $1 AND u.gender = $2
                LIMIT 1
            """
            params = (user_id, gender_preference)

        partner_rows = await db.execute(query, *params)

        if partner_rows:
            partner_id = partner_rows[0]['user_id']
            await db.execute_commit("DELETE FROM search_queue WHERE user_id IN ($1, $2)", user_id, partner_id)
            self.active_searches.discard(user_id)
            self.active_searches.discard(partner_id)
            return partner_id

        return None

    async def _create_chat(self, user1_id: int, user2_id: int) -> int:
        """Создает новый чат в базе данных"""
        await db.execute_commit("""
            INSERT INTO chats (user1_id, user2_id) VALUES ($1, $2)
        """, user1_id, user2_id)

        chat_rows = await db.execute("""
            SELECT chat_id FROM chats 
            WHERE user1_id = $1 AND user2_id = $2 
            ORDER BY started_at DESC LIMIT 1
        """, user1_id, user2_id)

        return chat_rows[0]['chat_id'] if chat_rows else None

    async def _pair_users(self, user1_id: int, user2_id: int, chat_id: int):
        """Связывает пользователей в чате"""
        await user_service.set_user_status(user1_id, 'chatting')
        await user_service.set_current_chat(user1_id, user2_id)

        await user_service.set_user_status(user2_id, 'chatting')
        await user_service.set_current_chat(user2_id, user1_id)

        await user_service.increment_chat_count(user1_id)
        await user_service.increment_chat_count(user2_id)

        logger.info(f"✅ Пользователи {user1_id} и {user2_id} соединены в чате {chat_id}")

    async def end_chat(self, user_id: int) -> int | None:
        """Завершает текущий чат"""
        partner_id = await user_service.get_current_chat(user_id)

        if partner_id:
            await user_service.set_user_status(user_id, 'menu')
            await user_service.set_current_chat(user_id, None)

            await user_service.set_user_status(partner_id, 'menu')
            await user_service.set_current_chat(partner_id, None)

            await db.execute_commit("""
                UPDATE chats SET ended_at = CURRENT_TIMESTAMP 
                WHERE (user1_id = $1 AND user2_id = $2) OR (user1_id = $3 AND user2_id = $4)
                AND ended_at IS NULL
            """, user_id, partner_id, partner_id, user_id)

            logger.info(f"💔 Чат между {user_id} и {partner_id} завершен")
            return partner_id

        return None

    async def cancel_search(self, user_id: int):
        """Отменяет поиск собеседника"""
        await db.execute_commit("DELETE FROM search_queue WHERE user_id = $1", user_id)
        await user_service.set_user_status(user_id, 'menu')
        self.active_searches.discard(user_id)
        logger.info(f"❌ Пользователь {user_id} отменил поиск")

    async def send_message(self, from_user_id: int, message_text: str) -> bool:
        """Отправляет сообщение собеседнику"""
        partner_id = await user_service.get_current_chat(from_user_id)

        if not partner_id:
            return False

        chat_rows = await db.execute("""
            SELECT chat_id FROM chats 
            WHERE (user1_id = $1 AND user2_id = $2) OR (user1_id = $3 AND user2_id = $4)
            AND ended_at IS NULL 
            ORDER BY started_at DESC LIMIT 1
        """, from_user_id, partner_id, partner_id, from_user_id)

        if chat_rows:
            chat_id = chat_rows[0]['chat_id']
            await db.execute_commit("""
                INSERT INTO messages (chat_id, user_id, text) 
                VALUES ($1, $2, $3)
            """, chat_id, from_user_id, message_text)
            return True

        return False

chat_service = ChatService()