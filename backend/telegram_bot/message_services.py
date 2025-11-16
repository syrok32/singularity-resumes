from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext
from .models import CommunicationSession, ChatMessage, TelegramProfile
from .services import _send_message
import logging

logger = logging.getLogger(__name__)

def handle_chat_message(update: Update, context: CallbackContext):
    """Обрабатывает сообщения в чате и пересылает их участникам"""
    message = update.message
    tg_user_id = message.from_user.id
    sessions = CommunicationSession.objects.filter(
        participants__profile__telegram_user_id=tg_user_id,
        session_status='active'
    )
    for session in sessions:
        chat_message = ChatMessage.objects.create(
            session=session,
            telegram_user_id=tg_user_id,
            text=message.text,
            message_type='text'
        )
        session.message_count += 1
        session.last_activity = timezone.now()
        session.save()
        forward_message_to_participants(session, chat_message)
        logger.info(f"Message forwarded in session #{session.id}")
        return True
    logger.warning(f"No active session for user {tg_user_id}")
    return False

def forward_message_to_participants(session, chat_message):
    """Пересылает сообщение всем участникам чата"""
    for participant in session.participants.all():
        if participant.profile.telegram_user_id == chat_message.telegram_user_id:
            continue
        forwarded_message = f"{get_user_display_name(chat_message.telegram_user_id)}: {chat_message.text}"
        _send_message(participant.profile.chat_id, forwarded_message)

def get_user_display_name(telegram_user_id):
    """Возвращает отображаемое имя пользователя"""
    try:
        profile = TelegramProfile.objects.get(telegram_user_id=telegram_user_id)
        return profile.user.get_full_name() or profile.username or f"User_{telegram_user_id}"
    except TelegramProfile.DoesNotExist:
        return f"User_{telegram_user_id}"