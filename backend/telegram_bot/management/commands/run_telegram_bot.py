from django.core.management.base import BaseCommand

from ...bots import run_polling


class Command(BaseCommand):
    help = 'Запускает Telegram-бота в режиме long polling (для локальной проверки)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot (polling)...'))
        run_polling()

