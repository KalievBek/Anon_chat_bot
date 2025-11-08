import logging
from services.chat_service import chat_service
from keyboards.main_keyboards import get_main_menu

logger = logging.getLogger(__name__)


def handle_reply_keyboard(update, context):
    """Обработка нажатий на reply-кнопки"""
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🔍 Найти собеседника":
        search_from_reply(update, context)
    elif text == "⏭️ Следующий":
        next_from_reply(update, context)
    elif text == "🚫 Завершить диалог":
        stop_from_reply(update, context)
    elif text == "👤 Профиль":
        profile_from_reply(update, context)
    elif text == "📋 Правила":
        rules_from_reply(update, context)
    elif text == "ℹ️ Помощь":
        help_from_reply(update, context)
    else:
        companion_id = chat_service.get_companion(user_id)
        if companion_id:
            try:
                context.bot.send_message(companion_id, f"💬 {text}")
            except Exception as e:
                update.message.reply_text("❌ Не удалось отправить сообщение")
        else:
            update.message.reply_text("❌ У вас нет активного чата", reply_markup=get_main_menu())


def search_from_reply(update, context):
    """Поиск из reply-кнопки"""
    user_id = update.effective_user.id
    companion = chat_service.get_companion(user_id)
    if companion:
        update.message.reply_text("❌ Вы уже в активном чате!", reply_markup=get_main_menu())
        return

    chat_service.add_to_search(user_id)
    update.message.reply_text("🔍 *Ищем собеседника...*", parse_mode='Markdown')

    companion_id = chat_service.find_companion(user_id)
    if companion_id:
        context.bot.send_message(user_id, "✅ *Собеседник найден!*", parse_mode='Markdown')
        context.bot.send_message(companion_id, "✅ *Собеседник найден!*", parse_mode='Markdown')


def next_from_reply(update, context):
    """Следующий из reply-кнопки"""
    user_id = update.effective_user.id
    companion_id = chat_service.end_chat(user_id)
    if companion_id:
        context.bot.send_message(companion_id, "🔁 *Собеседник перешел к следующему...*", parse_mode='Markdown')

    chat_service.add_to_search(user_id)
    update.message.reply_text("⏭️ *Ищем следующего собеседника...*", parse_mode='Markdown')

    companion_id = chat_service.find_companion(user_id)
    if companion_id:
        context.bot.send_message(user_id, "✅ *Новый собеседник найден!*", parse_mode='Markdown')


def stop_from_reply(update, context):
    """Стоп из reply-кнопки"""
    user_id = update.effective_user.id
    companion_id = chat_service.end_chat(user_id)
    if companion_id:
        context.bot.send_message(companion_id, "❌ *Собеседник завершил диалог*", parse_mode='Markdown')
    update.message.reply_text("💬 *Диалог завершен!*", parse_mode='Markdown')


def profile_from_reply(update, context):
    """Профиль из reply-кнопки"""
    from services.user_service import user_service
    from keyboards.main_keyboards import get_profile_keyboard
    user_id = update.effective_user.id
    profile_text = user_service.get_profile_text(user_id)
    update.message.reply_text(profile_text, reply_markup=get_profile_keyboard(), parse_mode='Markdown')


def rules_from_reply(update, context):
    """Правила из reply-кнопки"""
    rules_text = "📋 *Правила общения в чатах:*\n\n1. ✅ Уважайте собеседников\n2. ✅ Запрещен спам"
    update.message.reply_text(rules_text, reply_markup=get_main_menu(), parse_mode='Markdown')


def help_from_reply(update, context):
    """Помощь из reply-кнопки"""
    help_text = "ℹ️ *Помощь по боту:*\n\n💬 Нажми '🔍 Найти собеседника'"
    update.message.reply_text(help_text, reply_markup=get_main_menu(), parse_mode='Markdown')