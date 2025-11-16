
from django.utils import timezone
from datetime import timedelta
from .models import CommunicationSession
from .services import _send_message

def monitor_sessions():
    """Мониторинг неактивных сессий общения"""
    time_threshold = timezone.now() - timedelta(hours=72)
    inactive_sessions = CommunicationSession.objects.filter(
        session_status='active',
        last_activity__lte=time_threshold
    )
    for session in inactive_sessions:
        session.session_status = 'escalated'
        session.escalation_reason = '72 часа без активности'
        session.save()
        if session.chat_id:
            _send_message(session.chat_id, "Сессия эскалирована из-за неактивности.")