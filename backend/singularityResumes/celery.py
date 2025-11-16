# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'singularityResumes.settings')

app = Celery('singularityResumes')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    worker_pool='solo',  # Используем solo пул для Windows
    task_always_eager=False,
)
app.autodiscover_tasks()

# Расписание задач
app.conf.beat_schedule = {
    'check-sla-deadlines': {
        'task': 'telegram_bot.tasks.check_sla_deadlines',
        'schedule': 10,  # каждые 30 минут
    },
    'check-communication-sessions': {
        'task': 'telegram_bot.tasks.check_communication_sessions',
        'schedule': 3600,  # каждый час
    },
}