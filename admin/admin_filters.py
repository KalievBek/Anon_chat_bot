from aiogram.filters import BaseFilter
from aiogram.types import Message
from core.database import db


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        """Проверяет является ли пользователь администратором"""
        user_id = message.from_user.id

        try:
            # Проверяем в базе данных
            admin = await db.execute("SELECT * FROM admins WHERE user_id = $1", user_id)
            is_admin = bool(admin)

            if not is_admin:
                print(f"❌ Пользователь {user_id} не админ")
                # Отправляем сообщение что нет доступа
                await message.answer("❌ У вас нет доступа к админ-панели")

            return is_admin
        except Exception as e:
            print(f"❌ Ошибка проверки админа: {e}")
            return False