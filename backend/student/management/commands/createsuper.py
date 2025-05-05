from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Создаёт суперпользователя автоматически'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = 'admin'
        email = 'admin@ex.com'
        password = 'admin123123'  # Замените на более безопасный пароль

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" создан'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" уже существует'))
