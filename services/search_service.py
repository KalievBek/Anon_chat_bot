import logging
from core.database import db
from services.user_service import user_service

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.active_searches = set()

    async def start_search(self, user_id: int, gender_preference: str = 'any') -> dict:
        """Начинает поиск собеседника с учетом фильтра по полу"""
        try:
            # Добавляем пользователя в очередь поиска
            await self._add_to_search_queue(user_id, gender_preference)
            self.active_searches.add(user_id)
            await user_service.set_user_status(user_id, 'searching')

            # Ищем подходящего собеседника
            partner_id = await self._find_compatible_partner(user_id, gender_preference)

            if partner_id:
                return {
                    'success': True,
                    'partner_id': partner_id,
                    'message': '✅ Собеседник найден!'
                }
            else:
                return {
                    'success': False,
                    'partner_id': None,
                    'message': '⏳ Ищем подходящего собеседника...'
                }

        except Exception as e:
            logger.error(f"❌ Ошибка поиска для пользователя {user_id}: {e}")
            return {
                'success': False,
                'partner_id': None,
                'message': '❌ Ошибка поиска'
            }

    async def _add_to_search_queue(self, user_id: int, gender_preference: str):
        """Добавляет пользователя в очередь поиска"""
        await db.execute_commit("""
            INSERT INTO search_queue (user_id, gender_preference) 
            VALUES ($1, $2)
            ON CONFLICT (user_id) 
            DO UPDATE SET gender_preference = $2, created_at = CURRENT_TIMESTAMP
        """, user_id, gender_preference)

    async def _find_compatible_partner(self, user_id: int, gender_preference: str) -> int | None:
        """Ищет подходящего собеседника по фильтру"""
        if gender_preference == 'any':
            # Ищем любого собеседника
            query = """
                SELECT user_id FROM search_queue 
                WHERE user_id != $1 
                LIMIT 1
            """
            params = (user_id,)
        else:
            # Ищем собеседника с определенным полом
            query = """
                SELECT sq.user_id 
                FROM search_queue sq
                JOIN users u ON sq.user_id = u.user_id
                WHERE sq.user_id != $1 
                AND u.gender = $2
                LIMIT 1
            """
            params = (user_id, gender_preference)

        try:
            partner_rows = await db.execute(query, *params)

            if partner_rows:
                partner_id = partner_rows[0]['user_id']
                # Удаляем обоих из очереди поиска
                await self._remove_from_search_queue(user_id, partner_id)
                return partner_id

        except Exception as e:
            logger.error(f"❌ Ошибка поиска партнера: {e}")

        return None

    async def _remove_from_search_queue(self, user_id: int, partner_id: int = None):
        """Удаляет пользователей из очереди поиска"""
        if partner_id:
            await db.execute_commit("DELETE FROM search_queue WHERE user_id IN ($1, $2)", user_id, partner_id)
        else:
            await db.execute_commit("DELETE FROM search_queue WHERE user_id = $1", user_id)

        self.active_searches.discard(user_id)
        if partner_id:
            self.active_searches.discard(partner_id)

    async def cancel_search(self, user_id: int):
        """Отменяет поиск собеседника"""
        await self._remove_from_search_queue(user_id)
        await user_service.set_user_status(user_id, 'menu')
        logger.info(f"❌ Пользователь {user_id} отменил поиск")

    async def get_search_stats(self) -> dict:
        """Получает статистику поиска"""
        try:
            total_searches = await db.execute_scalar("SELECT COUNT(*) FROM search_queue")

            gender_stats = await db.execute("""
                SELECT u.gender, COUNT(*) as count
                FROM search_queue sq
                JOIN users u ON sq.user_id = u.user_id
                GROUP BY u.gender
            """)

            preference_stats = await db.execute("""
                SELECT gender_preference, COUNT(*) as count
                FROM search_queue
                GROUP BY gender_preference
            """)

            return {
                'total_searches': total_searches or 0,
                'gender_stats': {row['gender']: row['count'] for row in gender_stats},
                'preference_stats': {row['gender_preference']: row['count'] for row in preference_stats}
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики поиска: {e}")
            return {}


# Глобальный экземпляр
search_service = SearchService()