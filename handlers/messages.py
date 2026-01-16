from aiogram import Router, F
from aiogram.types import Message
from core.bot import bot
from handlers.commands import active_chats, searching_users
from services.chat_service import chat_service

router = Router()
from keyboards import main_menu_kb as main_kb


@router.message(F.text)  # Все текстовые сообщения
async def handle_all_messages(message: Message):
    user_id = message.from_user.id

    # 👇 ПРОПУСКАЕМ КОМАНДЫ (включая /admin)
    if message.text.startswith('/'):
        return

    # Если пользователь в активном чате - пересылаем и СОХРАНЯЕМ в БД
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            # Сохраняем сообщение в БД
            if message.text:
                await chat_service.send_message(user_id, message.text)

            # Пересылаем ВСЕ типы сообщений
            if message.text:
                await bot.send_message(partner_id, f"{message.text}")
            elif message.photo:
                await bot.send_photo(partner_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(partner_id, message.video.file_id, caption=message.caption)
            elif message.voice:
                await bot.send_voice(partner_id, message.voice.file_id)
            elif message.audio:
                await bot.send_audio(partner_id, message.audio.file_id)
            elif message.document:
                await bot.send_document(partner_id, message.document.file_id, caption=message.caption)
            elif message.sticker:
                await bot.send_sticker(partner_id, message.sticker.file_id)
            elif message.animation:
                await bot.send_animation(partner_id, message.animation.file_id)
            elif message.video_note:
                await bot.send_video_note(partner_id, message.video_note.file_id)
            elif message.contact:
                await bot.send_contact(partner_id, phone_number=message.contact.phone_number,
                                       first_name=message.contact.first_name)
            elif message.location:
                await bot.send_location(partner_id, latitude=message.location.latitude,
                                        longitude=message.location.longitude)
            else:
                await bot.send_message(partner_id, "📎 Собеседник отправил файл")

        except:
            # Если не удалось отправить, удаляем чат
            if user_id in active_chats:
                del active_chats[user_id]
            if partner_id in active_chats:
                del active_chats[partner_id]
            await message.answer("❌ Собеседник отключился", reply_markup=main_kb)

    # Если пользователь в поиске - игнорируем сообщения
    elif user_id in searching_users:
        pass

    # Если пользователь в меню - показываем подсказку
    else:
        await message.answer("🤔 Используйте кнопки меню для навигации", reply_markup=main_kb)