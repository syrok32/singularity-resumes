from django.conf import settings
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

from .handlers import start, register, accept, reject, on_callback

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("register", register))
application.add_handler(CommandHandler("accept", accept))
application.add_handler(CommandHandler("reject", reject))
application.add_handler(CallbackQueryHandler(on_callback, pattern=r'^(app|mod):(accept|reject):\d+$'))


def run_bot():
    application.run_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path=settings.TELEGRAM_BOT_TOKEN,
        webhook_url=f"http://{settings.DOMAIN}/telegram/webhook/{settings.TELEGRAM_BOT_TOKEN}"
    )


def run_polling():
    application.run_polling(allowed_updates=None, drop_pending_updates=True)
