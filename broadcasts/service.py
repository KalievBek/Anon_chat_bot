import logging
import json
from typing import List, Dict, Optional
from core.database import db

logger = logging.getLogger(__name__)


class BroadcastService:
    async def create_broadcast(self, admin_id: int, message_text: str,
                               message_type: str = 'text', file_id: str = None,
                               filters: Dict = None) -> int:
        """Создает новую рассылку"""
        try:
            filters_json = json.dumps(filters or {})

            logger.info(f"📢 Создание рассылки админом {admin_id}")
            logger.info(f"📝 Тип: {message_type}, Текст: {message_text[:50]}...")

            # ВСТАВЛЯЕМ рассылку и получаем ID
            await db.execute_commit("""
                INSERT INTO broadcasts (admin_id, message_text, message_type, file_id, filters, status, total_users)
                VALUES ($1, $2, $3, $4, $5, 'completed', $6)
            """, admin_id, message_text, message_type, file_id, filters_json, 0)

            # Получаем ID последней вставленной записи
            result = await db.execute("SELECT MAX(broadcast_id) as id FROM broadcasts")
            broadcast_id = result[0]['id'] if result and result[0]['id'] else 0

            logger.info(f"✅ Создана рассылка {broadcast_id} админом {admin_id}")
            return broadcast_id

        except Exception as e:
            logger.error(f"❌ Ошибка создания рассылки: {e}")
            return 0

    async def get_broadcast_stats(self, broadcast_id: int) -> Dict:
        """Получает статистику рассылки"""
        try:
            broadcast = await db.execute("""
                SELECT * FROM broadcasts WHERE broadcast_id = $1
            """, broadcast_id)

            if not broadcast:
                return None

            broadcast = dict(broadcast[0])

            # Статистика доставки
            status_stats = await db.execute("""
                SELECT status, COUNT(*) as count 
                FROM broadcast_status 
                WHERE broadcast_id = $1 
                GROUP BY status
            """, broadcast_id)

            stats = {
                'pending': 0,
                'delivered': 0,
                'failed': 0
            }

            for row in status_stats:
                stats[row['status']] = row['count']

            broadcast['delivery_stats'] = stats
            total_users = broadcast['total_users'] or 1
            broadcast['success_rate'] = (stats['delivered'] / total_users * 100) if total_users > 0 else 0

            return broadcast

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики рассылки: {e}")
            return None

    async def get_users_for_broadcast(self, filters: Dict = None) -> List[int]:
        """Получает список пользователей по фильтрам"""
        try:
            query = "SELECT user_id FROM users WHERE 1=1"
            params = []
            param_count = 0

            # Базовый фильтр - только активные пользователи
            query += " AND (status IS NULL OR status != 'banned')"

            if filters:
                if filters.get('min_age'):
                    param_count += 1
                    query += f" AND age >= ${param_count}"
                    params.append(filters['min_age'])

                if filters.get('max_age'):
                    param_count += 1
                    query += f" AND age <= ${param_count}"
                    params.append(filters['max_age'])

                if filters.get('gender') and filters['gender'] != 'any':
                    param_count += 1
                    query += f" AND gender = ${param_count}"
                    params.append(filters['gender'])

                if filters.get('min_chats'):
                    param_count += 1
                    query += f" AND total_chats >= ${param_count}"
                    params.append(filters['min_chats'])

                if filters.get('has_username'):
                    query += " AND username IS NOT NULL AND username != ''"

                # Лимит для тестирования
                if filters.get('limit'):
                    param_count += 1
                    query += f" LIMIT ${param_count}"
                    params.append(filters['limit'])

            logger.info(f"🔍 Запрос пользователей: {query}, params: {params}")
            users = await db.execute(query, *params)
            user_ids = [user['user_id'] for user in users]
            logger.info(f"👥 Найдено пользователей: {len(user_ids)}")
            return user_ids

        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователей: {e}")
            return []

    async def get_available_users_count(self) -> int:
        """Получает количество доступных пользователей"""
        try:
            users = await self.get_users_for_broadcast()
            return len(users)
        except Exception as e:
            logger.error(f"❌ Ошибка получения количества пользователей: {e}")
            return 0

    async def start_broadcast(self, broadcast_id: int, bot):
        """Запускает рассылку"""
        try:
            # Обновляем статус
            await db.execute_commit("""
                UPDATE broadcasts SET status = 'sending', sent_at = CURRENT_TIMESTAMP 
                WHERE broadcast_id = $1
            """, broadcast_id)

            # Получаем данные рассылки
            broadcast = await db.execute("SELECT * FROM broadcasts WHERE broadcast_id = $1", broadcast_id)
            if not broadcast:
                logger.error(f"❌ Рассылка {broadcast_id} не найдена")
                return

            broadcast = dict(broadcast[0])
            filters = json.loads(broadcast['filters'] or '{}')

            # Получаем пользователей
            user_ids = await self.get_users_for_broadcast(filters)
            total_users = len(user_ids)

            logger.info(f"📨 Начинаю рассылку {broadcast_id} для {total_users} пользователей")

            # Обновляем общее количество
            await db.execute_commit("""
                UPDATE broadcasts SET total_users = $1 WHERE broadcast_id = $2
            """, total_users, broadcast_id)

            # Создаем записи статусов (БЕЗ ON CONFLICT)
            for user_id in user_ids:
                # Сначала проверяем, существует ли уже запись
                existing = await db.execute("""
                    SELECT 1 FROM broadcast_status 
                    WHERE broadcast_id = $1 AND user_id = $2
                """, broadcast_id, user_id)

                if not existing:
                    await db.execute_commit("""
                        INSERT INTO broadcast_status (broadcast_id, user_id, status)
                        VALUES ($1, $2, 'pending')
                    """, broadcast_id, user_id)

            # Отправляем сообщения
            success_count = 0
            failed_count = 0

            for i, user_id in enumerate(user_ids):
                try:
                    if broadcast['message_type'] == 'text':
                        await bot.send_message(user_id, broadcast['message_text'])
                    elif broadcast['message_type'] == 'photo' and broadcast['file_id']:
                        await bot.send_photo(
                            user_id,
                            broadcast['file_id'],
                            caption=broadcast['message_text'] or None
                        )
                    elif broadcast['message_type'] == 'video' and broadcast['file_id']:
                        await bot.send_video(
                            user_id,
                            broadcast['file_id'],
                            caption=broadcast['message_text'] or None
                        )

                    await db.execute_commit("""
                        UPDATE broadcast_status SET status = 'delivered' 
                        WHERE broadcast_id = $1 AND user_id = $2
                    """, broadcast_id, user_id)
                    success_count += 1
                    logger.info(f"✅ Сообщение отправлено пользователю {user_id}")

                except Exception as e:
                    error_msg = str(e)[:100]
                    await db.execute_commit("""
                        UPDATE broadcast_status SET status = 'failed', error_message = $1
                        WHERE broadcast_id = $2 AND user_id = $3
                    """, error_msg, broadcast_id, user_id)
                    failed_count += 1
                    logger.warning(f"❌ Ошибка отправки пользователю {user_id}: {error_msg}")

                # Обновляем счетчик отправленных каждые 5 сообщений
                if i % 5 == 0:
                    await db.execute_commit("""
                        UPDATE broadcasts SET sent_count = $1 WHERE broadcast_id = $2
                    """, success_count, broadcast_id)

            # Финальное обновление счетчика
            await db.execute_commit("""
                UPDATE broadcasts SET sent_count = $1 WHERE broadcast_id = $2
            """, success_count, broadcast_id)

            # Завершаем рассылку
            await db.execute_commit("""
                UPDATE broadcasts SET status = 'completed' WHERE broadcast_id = $1
            """, broadcast_id)

            logger.info(
                f"✅ Рассылка {broadcast_id} завершена. Успешно: {success_count}/{total_users}, Ошибок: {failed_count}")

        except Exception as e:
            logger.error(f"❌ Критическая ошибка рассылки {broadcast_id}: {e}")
            # Помечаем рассылку как завершенную с ошибкой
            await db.execute_commit("""
                UPDATE broadcasts SET status = 'cancelled' WHERE broadcast_id = $1
            """, broadcast_id)

    async def get_admin_broadcasts(self, admin_id: int, limit: int = 10) -> List[Dict]:
        """Получает рассылки админа"""
        try:
            broadcasts = await db.execute("""
                SELECT * FROM broadcasts 
                WHERE admin_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            """, admin_id, limit)

            result = [dict(broadcast) for broadcast in broadcasts]
            logger.info(f"📋 Найдено рассылок для админа {admin_id}: {len(result)}")
            return result

        except Exception as e:
            logger.error(f"❌ Ошибка получения рассылок админа: {e}")
            return []

    async def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь админом"""
        try:
            admin = await db.execute("SELECT user_id FROM admins WHERE user_id = $1", user_id)
            is_admin = bool(admin)
            logger.info(f"🔐 Проверка админа {user_id}: {is_admin}")
            return is_admin
        except Exception as e:
            logger.error(f"❌ Ошибка проверки админа: {e}")
            # Для тестирования разрешите вашему ID
            return user_id == 2043400004

    async def add_admin(self, user_id: int, username: str, role: str = 'moderator'):
        """Добавляет админа"""
        try:
            await db.execute_commit("""
                INSERT INTO admins (user_id, username, role) 
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET
                username = $2,
                role = $3
            """, user_id, username, role)
            logger.info(f"✅ Добавлен админ: {user_id} (@{username})")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления админа: {e}")

    async def create_test_broadcast(self, admin_id: int) -> int:
        """Создает тестовую рассылку для проверки"""
        try:
            await db.execute_commit("""
                INSERT INTO broadcasts (admin_id, message_text, message_type, status, total_users, sent_count)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, admin_id, "Тестовая рассылка", "text", "completed", 10, 5)

            result = await db.execute("SELECT MAX(broadcast_id) as id FROM broadcasts")
            broadcast_id = result[0]['id'] if result and result[0]['id'] else 0
            logger.info(f"✅ Создана тестовая рассылка {broadcast_id}")
            return broadcast_id
        except Exception as e:
            logger.error(f"❌ Ошибка создания тестовой рассылки: {e}")
            return 0


# Глобальный экземпляр
broadcast_service = BroadcastService()