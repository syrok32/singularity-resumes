from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db import transaction
from student.models import Student, InternshipApplication
from telegram import Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler
from telegram_bot.models import TelegramProfile


async def start(update: Update, context: CallbackContext):
    tg_user = update.effective_user
    await update.message.reply_text(
        "Привет! Я бот платформы резюме.\n"
        "Команды:\n"
        "/register <email_пользователя> — привязать Telegram к аккаунту.\n"
        "/accept <id_заявки> — принять заявку.\n"
        "/reject <id_заявки> — отклонить заявку."
    )


async def register(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Укажи email: /register <email>")
        return

    email = context.args[0].strip().lower()
    tg = update.effective_user
    chat = update.effective_chat

    @transaction.atomic
    def register_sync() -> bool:
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return False

        TelegramProfile.objects.update_or_create(
            user=user,
            defaults={
                'telegram_user_id': tg.id,
                'chat_id': chat.id,
                'username': tg.username or '',
            }
        )
        Student.objects.filter(user=user).update(telegram_user_id=tg.id, telegram_chat_id=chat.id)
        return True

    ok = await sync_to_async(register_sync)()
    if not ok:
        await update.message.reply_text("Пользователь с таким email не найден")
        return
    await update.message.reply_text("Готово! Telegram привязан к аккаунту.")


async def accept(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Укажи id заявки: /accept <id>")
        return
    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Некорректный id")
        return

    tg_user_id = update.effective_user.id

    @transaction.atomic
    def accept_sync():
        application = InternshipApplication.objects.filter(id=app_id).select_related('student', 'student__user').first()
        if not application:
            return None, "Заявка не найдена"
        is_student = application.student.telegram_user_id == tg_user_id
        is_moderator = TelegramProfile.objects.filter(telegram_user_id=tg_user_id, is_moderator=True).exists()
        if is_student:
            application.student_response = 'accepted'
        elif is_moderator:
            application.moderator_response = 'accepted'
        else:
            return None, "Нет прав для принятия этой заявки"
        application.save()
        return application, None

    application, err = await sync_to_async(accept_sync)()
    if err:
        await update.message.reply_text(err)
        return
    await update.message.reply_text(f"Заявка #{application.id}: статус {application.status}")


async def reject(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Укажи id заявки: /reject <id>")
        return
    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Некорректный id")
        return

    tg_user_id = update.effective_user.id

    @transaction.atomic
    def reject_sync():
        application = InternshipApplication.objects.filter(id=app_id).select_related('student', 'student__user').first()
        if not application:
            return None, "Заявка не найдена"
        is_student = application.student.telegram_user_id == tg_user_id
        is_moderator = TelegramProfile.objects.filter(telegram_user_id=tg_user_id, is_moderator=True).exists()
        if is_student:
            application.student_response = 'rejected'
        elif is_moderator:
            application.moderator_response = 'rejected'
        else:
            return None, "Нет прав для отклонения этой заявки"
        application.save()
        return application, None

    application, err = await sync_to_async(reject_sync)()
    if err:
        await update.message.reply_text(err)
        return
    await update.message.reply_text(f"Заявка #{application.id}: статус {application.status}")


async def on_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = (query.data or '').split(':')
    if len(data) != 3:
        return
    scope, action, raw_id = data
    try:
        app_id = int(raw_id)
    except ValueError:
        return

    tg_user_id = query.from_user.id

    @transaction.atomic
    def apply_action():
        application = InternshipApplication.objects.filter(id=app_id).select_related('student').first()
        if not application:
            return None, 'Заявка не найдена'
        if scope == 'app':
            # student
            if application.student.telegram_user_id != tg_user_id:
                return None, 'Недостаточно прав'
            application.student_response = 'accepted' if action == 'accept' else 'rejected'
        elif scope == 'mod':
            # moderator
            is_moderator = TelegramProfile.objects.filter(telegram_user_id=tg_user_id, is_moderator=True).exists()
            if not is_moderator:
                return None, 'Недостаточно прав'
            application.moderator_response = 'accepted' if action == 'accept' else 'rejected'
        else:
            return None, 'Ошибка'
        application.save()
        return application, None

    application, err = await sync_to_async(apply_action)()
    if err:
        await query.edit_message_text(err)
        return
    await query.edit_message_text(f"Заявка #{application.id}: статус {application.status}")
