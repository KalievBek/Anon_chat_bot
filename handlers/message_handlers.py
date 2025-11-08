from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Filter

from services.user_service import user_service
from core.bot import bot

router = Router()

class IsChatting(Filter):
    async def __call__(self, message: Message) -> bool:
        status = await user_service.get_user_status(message.from_user.id)
        return status == 'chatting'

# Обработчик для сообщений в чате
@router.message(IsChatting())
async def handle_chat_message(message: Message):
    user_id = message.from_user.id
    partner_id = await user_service.get_current_chat(user_id)

    if partner_id:
        try:
            await message.copy_to(partner_id)
        except Exception as e:
            await message.answer("Не удалось отправить сообщение. Возможно, ваш собеседник заблокировал бота.")
            await user_service.set_user_status(user_id, 'menu')
    else:
        await message.answer("Ошибка: Чат не найден. Попробуйте снова начать поиск.")
        await user_service.set_user_status(user_id, 'menu')