"""
Модели Telegram-бота для платформы Resume Student
=================================================
Описывает структуру данных для:
- Профили пользователей Telegram
- Сессии общения между HR, студентами и кураторами
- Участники чатов
- Сообщения в чатах
"""

from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    """
    Профиль пользователя в Telegram
    Связывает Django User с Telegram ID
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='telegram_profile'
    )
    telegram_user_id = models.BigIntegerField(unique=True, db_index=True)
    chat_id = models.BigIntegerField()
    username = models.CharField(max_length=255, blank=True)
    is_moderator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Telegram профиль'
        verbose_name_plural = 'Telegram профили'
        indexes = [
            models.Index(fields=['telegram_user_id']),
            models.Index(fields=['is_moderator']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name() or self.user.email} (TG: {self.telegram_user_id})"
        return f"{self.username or 'Unknown'} (TG: {self.telegram_user_id})"


class CommunicationSession(models.Model):
    """
    Сессия общения для заявки
    Объединяет HR, студента и куратора в одном чате
    """
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('escalated', 'На эскалации'),
    ]

    application = models.OneToOneField(
        'student.InternshipApplication',
        on_delete=models.CASCADE,
        related_name='communication_session'
    )
    chat_id = models.BigIntegerField(default=0)
    session_started = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    message_count = models.IntegerField(default=0)
    session_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    escalation_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Сессия общения'
        verbose_name_plural = 'Сессии общения'
        indexes = [
            models.Index(fields=['session_status', 'last_activity']),
        ]

    def __str__(self):
        return f"Сессия #{self.id} для заявки #{self.application_id} ({self.session_status})"


class ChatParticipant(models.Model):
    """
    Участник чата
    Определяет роль пользователя в конкретной сессии
    """
    ROLE_CHOICES = [
        ('employer', 'Работодатель'),
        ('student', 'Студент'),
        ('curator', 'Куратор'),
    ]

    session = models.ForeignKey(
        CommunicationSession,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    profile = models.ForeignKey(
        TelegramProfile,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'profile']
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чатов'
        indexes = [
            models.Index(fields=['session', 'role']),
        ]

    def __str__(self):
        return f"{self.get_role_display()}: {self.profile.username} в сессии #{self.session_id}"


class ChatMessage(models.Model):
    """
    Сообщение в чате
    Хранит историю переписки
    """
    session = models.ForeignKey(
        CommunicationSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    telegram_user_id = models.BigIntegerField()
    text = models.TextField()
    message_type = models.CharField(max_length=20, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]

    def __str__(self):
        return f"Сообщение в сессии #{self.session_id} от {self.telegram_user_id}"
