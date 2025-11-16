"""
Конфигурация приложения student.
"""

from django.apps import AppConfig


class StudentConfig(AppConfig):
    """Конфигурация приложения для управления студентами."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'student'
    verbose_name = 'Студенты и резюме'

    def ready(self):
        """
        Выполняется при инициализации приложения.
        Здесь можно регистрировать сигналы, задачи Celery и т.д.
        """
        # Импорт сигналов (если будут добавлены)
        try:
            import student.signals  # noqa
        except ImportError:
            pass

        # Регистрация задач Celery (если будут добавлены)
        try:
            import student.tasks  # noqa
        except ImportError:
            pass
