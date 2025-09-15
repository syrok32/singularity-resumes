from django.contrib import admin
from .models import TelegramProfile


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "telegram_user_id", "chat_id", "is_moderator", "updated_at")
    list_filter = ("is_moderator",)
    search_fields = ("user__email", "user__username", "telegram_user_id", "username")
    readonly_fields = ("created_at", "updated_at")

