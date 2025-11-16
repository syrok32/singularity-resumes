"""
Сигналы для приложения student.
Обработка событий изменения данных.
"""

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache

from .models import Student, Skill, Specialty, SkillCategory
from .api_views import invalidate_filter_options_cache, invalidate_stats_cache


@receiver(post_save, sender=Student)
def invalidate_cache_on_student_save(sender, instance, created, **kwargs):
    """
    Инвалидирует кеш при создании или обновлении студента.
    """
    invalidate_stats_cache()

    # Если изменился статус активности, сбрасываем фильтры
    if not created and hasattr(instance, '_previous_is_active'):
        if instance._previous_is_active != instance.is_active:
            invalidate_filter_options_cache()


@receiver(post_delete, sender=Student)
def invalidate_cache_on_student_delete(sender, instance, **kwargs):
    """Инвалидирует кеш при удалении студента."""
    invalidate_stats_cache()
    invalidate_filter_options_cache()


@receiver([post_save, post_delete], sender=Skill)
@receiver([post_save, post_delete], sender=Specialty)
@receiver([post_save, post_delete], sender=SkillCategory)
def invalidate_cache_on_reference_change(sender, instance, **kwargs):
    """
    Инвалидирует кеш при изменении справочников
    (навыки, специальности, категории).
    """
    invalidate_filter_options_cache()
    invalidate_stats_cache()


@receiver(m2m_changed, sender=Student.skills.through)
def invalidate_cache_on_skills_change(sender, instance, action, **kwargs):
    """Инвалидирует кеш при изменении навыков студента."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        invalidate_stats_cache()
