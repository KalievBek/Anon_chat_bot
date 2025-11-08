# handlers/callback_handlers.py
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.chat_service import chat_service
from services.user_service import user_service
from keyboards.main_keyboards import main_menu_kb

router = Router()


@router.callback_query(F.data == "cancel_search")
async def process_cancel_search(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_status = await user_service.get_user_status(user_id)

    if current_status == 'searching':
        await chat_service.end_chat(user_id)
        # Редактируем сообщение (убираем кнопку)
        await callback_query.message.edit_text(
            "❌ Поиск отменен.",
            reply_markup=None
        )
        await callback_query.message.answer("Главное меню.", reply_markup=main_menu_kb)
    else:
        # Если статус уже не 'searching', просто удаляем сообщение
        # Дополнительная проверка, чтобы избежать ошибки, если сообщение уже удалено
        try:
            await callback_query.message.delete()
        except Exception:
            pass

    await callback_query.answer()  # Закрываем уведомление на клиенте