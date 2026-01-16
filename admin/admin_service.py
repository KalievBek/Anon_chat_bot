import logging
from typing import List, Dict, Any
from .admin_models import DashboardStats, UserStats, SystemMetrics
from core.database import db

logger = logging.getLogger(__name__)


class AdminService:
    async def get_dashboard_stats(self) -> DashboardStats:
        """Получает статистику для дашборда"""
        try:
            total_users = await db.execute_scalar("SELECT COUNT(*) FROM users")

            active_today = await db.execute_scalar("""
                SELECT COUNT(DISTINCT user_id) FROM (
                    SELECT user1_id as user_id FROM chats WHERE started_at >= CURRENT_DATE
                    UNION 
                    SELECT user2_id as user_id FROM chats WHERE started_at >= CURRENT_DATE
                    UNION
                    SELECT user_id FROM search_queue
                ) AS active_users
            """)

            active_chats_now = await db.execute_scalar("""
                SELECT COUNT(*) FROM chats WHERE ended_at IS NULL
            """)

            searches_now = await db.execute_scalar("SELECT COUNT(*) FROM search_queue")

            messages_today = await db.execute_scalar("""
                SELECT COUNT(*) FROM messages 
                WHERE sent_at >= CURRENT_DATE
            """)

            avg_rating = await db.execute_scalar("SELECT AVG(rating) FROM users WHERE rating > 0")

            reports_pending = await db.execute_scalar("""
                SELECT COUNT(*) FROM reports WHERE status = 'pending'
            """) or 0

            return DashboardStats(
                total_users=total_users or 0,
                active_today=active_today or 0,
                active_chats_now=active_chats_now or 0,
                searches_now=searches_now or 0,
                messages_today=messages_today or 0,
                avg_rating=round(avg_rating or 5.0, 1),
                reports_pending=reports_pending
            )

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return DashboardStats(0, 0, 0, 0, 0, 5.0, 0)

    async def get_problematic_users(self, limit: int = 10) -> List[UserStats]:
        """Получает пользователей с низким рейтингом"""
        try:
            rows = await db.execute("""
                SELECT user_id, username, rating, total_chats, created_at
                FROM users 
                WHERE rating < 3 
                ORDER BY rating ASC, total_chats DESC
                LIMIT $1
            """, limit)

            return [
                UserStats(
                    user_id=row['user_id'],
                    username=row['username'] or 'без username',
                    rating=float(row['rating'] or 5.0),
                    total_chats=row['total_chats'] or 0,
                    created_at=str(row['created_at'])[:10],
                    last_active='сегодня'  # можно добавить реальные данные
                ) for row in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка получения проблемных пользователей: {e}")
            return []

    async def get_gender_stats(self) -> Dict[str, int]:
        """Статистика по полу"""
        try:
            rows = await db.execute("""
                SELECT gender, COUNT(*) as count 
                FROM users 
                GROUP BY gender
            """)

            return {row['gender']: row['count'] for row in rows}
        except Exception as e:
            logger.error(f"Ошибка получения гендерной статистики: {e}")
            return {}

    async def get_top_users(self, limit: int = 5) -> List[UserStats]:
        """Топ пользователей по рейтингу"""
        try:
            rows = await db.execute("""
                SELECT user_id, username, rating, total_chats, created_at
                FROM users 
                WHERE rating >= 7 AND total_chats > 5
                ORDER BY rating DESC, total_chats DESC
                LIMIT $1
            """, limit)

            return [
                UserStats(
                    user_id=row['user_id'],
                    username=row['username'] or 'без username',
                    rating=float(row['rating']),
                    total_chats=row['total_chats'],
                    created_at=str(row['created_at'])[:10],
                    last_active='активен'
                ) for row in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка получения топ пользователей: {e}")
            return []

    async def ban_user(self, user_id: int, reason: str = "Нарушение правил"):
        """Блокировка пользователя"""
        try:
            await db.execute_commit("""
                INSERT INTO banned_users (user_id, reason, banned_at) 
                VALUES ($1, $2, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET reason = $2, banned_at = CURRENT_TIMESTAMP
            """, user_id, reason)

            # Удаляем из активных чатов и поиска
            await db.execute_commit("DELETE FROM search_queue WHERE user_id = $1", user_id)
            return True
        except Exception as e:
            logger.error(f"Ошибка бана пользователя {user_id}: {e}")
            return False

    async def get_system_metrics(self) -> SystemMetrics:
        """Системные метрики"""
        # Заглушка - в реальности брать из мониторинга
        return SystemMetrics(
            db_connections=10,
            memory_usage=45.2,
            response_time=0.8,
            errors_last_hour=2
        )


admin_service = AdminService()