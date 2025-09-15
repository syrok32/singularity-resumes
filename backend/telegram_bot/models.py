from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_profile',
        verbose_name='Пользователь'
    )
    telegram_user_id = models.BigIntegerField(unique=True, verbose_name='Telegram user id')
    chat_id = models.BigIntegerField(verbose_name='Chat id')
    username = models.CharField(max_length=255, blank=True, verbose_name='TG username')
    is_moderator = models.BooleanField(default=False, verbose_name='Куратор')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} ↔ {self.telegram_user_id}"

    class Meta:
        verbose_name = 'Telegram профиль'
        verbose_name_plural = 'Telegram профили'
