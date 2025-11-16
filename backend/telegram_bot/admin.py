"""
Настройка Django Admin для управления ботом
============================================
"""

from django.contrib import admin
from .models import TelegramProfile, CommunicationSession, ChatParticipant, ChatMessage


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ['telegram_user_id', 'username', 'user', 'is_moderator', 'created_at']
    list_filter = ['is_moderator', 'created_at']
    search_fields = ['telegram_user_id', 'username', 'user__email']


@admin.register(CommunicationSession)
class CommunicationSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'session_status', 'message_count', 'last_activity']
    list_filter = ['session_status', 'session_started']
    search_fields = ['application__id', 'application__student__full_name']


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ['session', 'profile', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'telegram_user_id', 'text_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Текст'
