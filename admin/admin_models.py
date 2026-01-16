from dataclasses import dataclass
from typing import Dict, List, Any
from datetime import datetime

@dataclass
class DashboardStats:
    total_users: int
    active_today: int
    active_chats_now: int
    searches_now: int
    messages_today: int
    avg_rating: float
    reports_pending: int

@dataclass
class UserStats:
    user_id: int
    username: str
    rating: float
    total_chats: int
    created_at: str
    last_active: str

@dataclass
class SystemMetrics:
    db_connections: int
    memory_usage: float
    response_time: float
    errors_last_hour: int