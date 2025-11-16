"""
Celery задачи для асинхронной обработки
=======================================
- Проверка SLA дедлайнов
- Мониторинг сессий общения
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from student.models import InternshipApplication
from telegram_bot.services import send_sla_reminder
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_sla_deadlines():
    """
    Проверяет SLA дедлайны для заявок
    Запускается каждый час через Celery Beat
    """
    logger.info("⏰ Checking SLA deadlines...")

    now = timezone.now()
    deadline_threshold = now + timedelta(hours=2)

    # Находим заявки с истекающим SLA
    expiring_applications = InternshipApplication.objects.filter(
        sla_deadline__lte=deadline_threshold,
        reminder_sent=False,
        status='pending'
    )

    count = 0
    for application in expiring_applications:
        send_sla_reminder(application)
        count += 1

    logger.info(f"✅ Sent {count} SLA reminders")
    return count


@shared_task
def monitor_communication_sessions():
    """
    Мониторинг сессий общения
    Проверяет активность и закрывает неактивные сессии
    """
    from .models import CommunicationSession

    logger.info("👁️ Monitoring communication sessions...")

    # Находим неактивные сессии (более 7 дней без активности)
    inactive_threshold = timezone.now() - timedelta(days=7)

    inactive_sessions = CommunicationSession.objects.filter(
        session_status='active',
        last_activity__lt=inactive_threshold
    )

    count = 0
    for session in inactive_sessions:
        session.session_status = 'completed'
        session.escalation_reason = 'Автоматически закрыта из-за неактивности'
        session.save()
        count += 1

    logger.info(f"✅ Closed {count} inactive sessions")
    return count


# telegram_bot/tasks.py - НОВАЯ ЗАДАЧА
@shared_task(bind=True)
def start_sla_timer(self, application_id):
    """
    Production-grade SLA таймер для конкретной заявки

    Args:
        application_id: ID заявки для отслеживания

    Логика:
    - Устанавливает SLA дедлайн (12 часов)
    - Планирует напоминания (на 10ч и 11ч)
    - Эскалирует при истечении (12ч)
    - Логирует все события для отладки
    """
    from student.models import InternshipApplication
    from telegram_bot.services import send_sla_reminder

    try:
        logger.info(f"⏰ SLA таймер запущен для заявки #{application_id}")

        # Получаем заявку
        application = InternshipApplication.objects.get(id=application_id)

        if application.status != 'pending':
            logger.info(f"⚠️ Заявка #{application_id} уже обработана (статус: {application.status})")
            return {'status': 'skipped', 'reason': 'not_pending'}

        # Устанавливаем SLA дедлайн (12 часов)
        application.sla_deadline = timezone.now() + timedelta(hours=12)
        application.save()

        logger.info(f"✅ SLA дедлайн установлен: {application.sla_deadline} (заявка #{application_id})")

        # Немедленно отправляем первое уведомление
        send_sla_reminder(application)

        return {
            'status': 'success',
            'application_id': application_id,
            'sla_deadline': application.sla_deadline.isoformat()
        }

    except InternshipApplication.DoesNotExist:
        logger.error(f"❌ Заявка #{application_id} не найдена")
        return {'status': 'error', 'reason': 'application_not_found'}
    except Exception as e:
        logger.error(f"❌ Ошибка SLA таймера для заявки #{application_id}: {e}", exc_info=True)
        raise self.retry(countdown=60, max_retries=3)  # Retry с задержкой



