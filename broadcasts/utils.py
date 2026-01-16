from aiogram.exceptions import TelegramBadRequest

async def safe_edit_message(callback, text, reply_markup=None):
    """Безопасное редактирование сообщения"""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("✅")
            return False
        else:
            raise e