"""
Главный файл Telegram-бота
===========================
Регистрация всех обработчиков и запуск бота
"""

from django.conf import settings
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters
)
from .handlers import (
    start,
    register,
    accept,
    reject,
    join_chat,
    close_session,
    handle_chat_message
)
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================================================

def create_bot_application() -> Application:
    """
    Создает и настраивает приложение бота

    Returns:
        Application: Настроенное приложение бота
    """
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # ========================================================================
    # РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ КОМАНД
    # ========================================================================

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("accept", accept))
    application.add_handler(CommandHandler("reject", reject))
    application.add_handler(CommandHandler("join_chat", join_chat))
    application.add_handler(CommandHandler("close_session", close_session))

    # ========================================================================
    # ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (ЧАТ)
    # ========================================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_chat_message
        )
    )

    # ========================================================================
    # ОБРАБОТЧИК ОШИБОК
    # ========================================================================

    async def error_handler(update: Update, context: CallbackContext):
        """Глобальный обработчик ошибок"""
        logger.error(
            f"❌ Exception while handling update: {context.error}",
            exc_info=context.error
        )

        error_text = (
            "❌ Произошла ошибка при обработке запроса.\n"
            "Попробуйте позже или обратитесь к администратору."
        )

        try:
            if update and update.message:
                await update.message.reply_text(error_text)
            elif update and update.callback_query:
                await update.callback_query.message.reply_text(error_text)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    application.add_error_handler(error_handler)

    logger.info("✅ Bot application configured successfully")
    return application


# ============================================================================
# ЗАПУСК БОТА
# ============================================================================

def run_polling():
    """
    Запускает бота в режиме polling (опрос сервера Telegram)
    Рекомендуется для разработки
    """
    application = create_bot_application()
    logger.info("🚀 Starting bot in POLLING mode...")
    application.run_polling(drop_pending_updates=True)


def run_webhook(webhook_url: str, port: int = 8443):
    """
    Запускает бота в режиме webhook
    Рекомендуется для production

    Args:
        webhook_url: URL для webhook (https://your-domain.com/webhook)
        port: Порт для прослушивания
    """
    application = create_bot_application()
    logger.info(f"🚀 Starting bot in WEBHOOK mode on {webhook_url}:{port}...")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=settings.TELEGRAM_BOT_TOKEN,
        webhook_url=f"{webhook_url}/{settings.TELEGRAM_BOT_TOKEN}"
    )


# ============================================================================
# ЭКСПОРТ
# ============================================================================

# Создаем глобальный экземпляр приложения
application = create_bot_application()
