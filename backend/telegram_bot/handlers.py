"""
Обработчики команд Telegram-бота
=================================
Содержит все команды бота:
- /start - Приветствие и начало работы
- /register - Привязка Telegram к аккаунту
- /accept - Принять заявку
- /reject - Отклонить заявку
- /join_chat - Присоединиться к чату
- /close_session - Завершить сессию
"""

import logging
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from student.models import InternshipApplication, Student
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot.models import TelegramProfile, CommunicationSession, ChatParticipant
from telegram_bot.services import (
    send_telegram_message,
    create_communication_chat,
    requires_curator_approval
)

logger = logging.getLogger(__name__)


# ============================================================================
# КОМАНДА /START
# ============================================================================


async def handle_employer_first_login(update: Update, context: CallbackContext, param: str):
    """
    Production-grade обработчик первого входа работодателя

    Формат: /start employer_123_abc123def456
    Где:
    - 123 = application.id
    - abc123def456 = tracking_token (безопасность)
    """
    try:
        parts = param.split('_')
        if len(parts) != 3:
            await update.message.reply_text("❌ Некорректная ссылка.")
            return

        app_id = int(parts[1])
        tracking_token = parts[2]

        # Получаем заявку с токеном верификации
        application = await sync_to_async(
            lambda: InternshipApplication.objects.select_related(
                'student', 'employer'
            ).get(id=app_id, tracking_token=tracking_token)
        )()

        tg_user = update.effective_user
        chat = update.effective_chat

        # Создаем профиль работодателя (если не существует)
        employer_profile, created = await sync_to_async(
            lambda: TelegramProfile.objects.update_or_create(
                telegram_user_id=tg_user.id,
                defaults={
                    'chat_id': chat.id,
                    'username': f"{tg_user.first_name} {tg_user.last_name}".strip() or tg_user.username or application.employer.name,
                    'is_moderator': False,
                    'role': 'employer'
                }
            )
        )()

        # Привязываем профиль к работодателю
        if application.employer.telegram_id == str(tg_user.id):
            # Уже привязан
            pass
        else:
            # Обновляем telegram_id работодателя
            application.employer.telegram_id = str(tg_user.id)
            await sync_to_async(application.employer.save)()

        # Отмечаем успешную регистрацию
        application.employer_registered = True
        application.employer_telegram_user_id = tg_user.id
        await sync_to_async(application.save)()

        # Production-ready приветствие с персонализацией
        welcome_message = (
            f"🎯 <b>Добро пожаловать в Resume Student Bot!</b>\n\n"
            f"👋 <i>Привет, {tg_user.first_name}!</i>\n\n"
            f"✅ Вы успешно вошли как <b>работодатель</b> для заявки <code>#{application.id}</code>\n\n"
            f"📋 <b>Детали вашей заявки:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        if application.status == 'pending':
            welcome_message += (
                f"⏳ <b>Статус:</b> Ожидается ответ студента\n"
                f"👨‍🎓 <b>Студент:</b> {application.student.full_name}\n"
                f"🎓 <b>Курс:</b> {application.student.course}\n"
                f"🏢 <b>Ваша компания:</b> {application.company_name}\n\n"
                f"🔔 <b>Что будет дальше:</b>\n"
                f"• Студент получит уведомление (12ч SLA)\n"
                f"• При принятии заявки создастся чат\n"
                f"• Вы получите уведомление о статусе\n\n"
                f"📱 <b>Уведомления включены</b>\n"
                f"Вы будете получать все обновления по этой заявке."
            )
        elif application.status == 'accepted':
            welcome_message += (
                f"🎉 <b>Статус:</b> Студент принял заявку!\n"
                f"👨‍🎓 <b>Студент:</b> {application.student.full_name}\n"
                f"🏢 <b>Ваша компания:</b> {application.company_name}\n\n"
                f"💬 <b>Присоединиться к чату:</b>\n"
                f"<code>/join_chat {application.id}</code>\n\n"
                f"📱 <b>Уведомления включены</b>"
            )
        else:
            welcome_message += (
                f"❌ <b>Статус:</b> Заявка отклонена\n"
                f"👨‍🎓 <b>Студент:</b> {application.student.full_name}\n"
                f"🏢 <b>Ваша компания:</b> {application.company_name}"
            )

        welcome_message += "\n\n🤖 <i>Resume Student Bot | Поддержка: @your_support</i>"

        # Отправляем с HTML-разметкой
        await update.message.reply_text(
            welcome_message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        # Добавляем inline-кнопки (если заявка принята)
        if application.status == 'accepted' and not application.chat_created:
            keyboard = [
                [InlineKeyboardButton("💬 Присоединиться к чату", callback_data=f"join_{application.id}")],
                [InlineKeyboardButton("ℹ️ Статус заявки", callback_data=f"status_{application.id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "🎯 <b>Быстрые действия:</b>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )

        # Отправляем админу уведомление о новом работодателе (для аналитики)
        admin_notification = (
            f"🆕 <b>Новый работодатель зарегистрирован</b>\n\n"
            f"👤 <b>Имя:</b> {employer_name}\n"
            f"🏢 <b>Компания:</b> {company}\n"
            f"📧 <b>Email:</b> {employer_email}\n"
            f"📱 <b>Telegram:</b> {tg_user.id}\n"
            f"🆔 <b>Заявка:</b> #{application.id}\n"
            f"👨‍🎓 <b>Студент:</b> {student_name}"
        )

        # Отправляем админам
        for admin in TelegramProfile.objects.filter(is_moderator=True):
            send_telegram_message(admin.chat_id, admin_notification, parse_mode='HTML')

        logger.info(f"🎉 Работодатель {tg_user.id} успешно зарегистрирован для заявки #{application.id}")

    except (ValueError, IndexError):
        logger.error(f"❌ Некорректный формат employer deep-link: {param}")
        await update.message.reply_text(
            "❌ <b>Ошибка доступа</b>\n\n"
            "Эта ссылка недействительна или истекла.\n"
            "Обратитесь в поддержку или создайте новую заявку на сайте.",
            parse_mode='HTML'
        )
    except InternshipApplication.DoesNotExist:
        logger.error(f"❌ Заявка #{app_id} не найдена или токен недействителен")
        await update.message.reply_text(
            "❌ <b>Заявка не найдена</b>\n\n"
            "Эта заявка либо удалена, либо ссылка недействительна.\n"
            "Создайте новую заявку на сайте Resume Student.",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации работодателя: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ <b>Внутренняя ошибка</b>\n\n"
            "Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.",
            parse_mode='HTML'
        )
async def start(update: Update, context: CallbackContext):
    """
    Обрабатывает /start с параметром employer_123
    """
    tg_user = update.effective_user
    chat = update.effective_chat

    logger.info(f"🚀 /start from user {tg_user.id}, args: {context.args}")

    # Проверяем параметры
    if context.args:
        param = context.args[0]

        # НОВЫЙ ОБРАБОТЧИК для работодателя
        if param.startswith('employer_'):
            await handle_employer_registration(update, context, param)
            return

        # Существующие обработчики
        if param.startswith('application_'):
            await handle_application_link(update, context, param)
            return

        if param.startswith('chat_'):
            await handle_chat_link(update, context, param)
            return

    # Обычное приветствие
    welcome_text = (
        f"👋 Привет, {tg_user.first_name}!\n\n"
        f"Я бот платформы Resume Student.\n\n"
        f"📋 Доступные команды:\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"/register <email> - Привязать аккаунт\n"
        f"/accept <id> - Принять заявку\n"
        f"/reject <id> - Отклонить заявку"
    )

    await update.message.reply_text(welcome_text)


async def handle_employer_registration(update: Update, context: CallbackContext, param: str):
    """
    НОВАЯ ФУНКЦИЯ: Регистрация работодателя при первом входе
    """
    try:
        app_id = int(param.split('_')[1])
        application = await sync_to_async(
            lambda: InternshipApplication.objects.select_related(
                'student', 'employer'
            ).get(id=app_id)
        )()

        tg_user = update.effective_user
        chat = update.effective_chat

        # Создаем или обновляем профиль работодателя
        employer_profile, created = await sync_to_async(
            lambda: TelegramProfile.objects.update_or_create(
                telegram_user_id=tg_user.id,
                defaults={
                    'chat_id': chat.id,
                    'username': tg_user.username or tg_user.first_name or application.employer.name,
                    'is_moderator': False
                }
            )
        )()

        # Связываем работодателя с заявкой
        application.employer.telegram_id = str(tg_user.id)
        await sync_to_async(application.employer.save)()

        # Приветственное сообщение
        welcome_text = (
            f"👋 Добро пожаловать, {tg_user.first_name}!\n\n"
            f"✅ Вы успешно зарегистрированы как работодатель.\n\n"
            f"📋 Ваша заявка #{app_id}:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👨🎓 Студент: {application.student.full_name}\n"
            f"📊 Статус: {application.status}\n\n"
        )

        if application.status == 'pending':
            welcome_text += (
                f"⏳ Ожидается ответ студента.\n"
                f"Вы получите уведомление, когда студент примет или отклонит заявку."
            )
        elif application.status == 'accepted':
            welcome_text += (
                f"🎉 Студент принял вашу заявку!\n"
                f"Используйте команду /join_chat {app_id} для начала общения."
            )
        elif application.status == 'rejected':
            welcome_text += f"❌ К сожалению, студент отклонил заявку."

        await update.message.reply_text(welcome_text)

        logger.info(f"✅ Employer {tg_user.id} registered for application #{app_id}")

    except (ValueError, IndexError, InternshipApplication.DoesNotExist):
        await update.message.reply_text("❌ Некорректная ссылка.")
        logger.error(f"Invalid employer link: {param}")

async def handle_application_link(update: Update, context: CallbackContext, param: str):
    """Обрабатывает переход по ссылке к заявке"""
    try:
        app_id = int(param.split('_')[1])
        application = await sync_to_async(
            lambda: InternshipApplication.objects.get(id=app_id)
        )()

        tg_user = update.effective_user

        # Проверяем права доступа
        if application.telegram_user_id == str(tg_user.id):
            await update.message.reply_text(
                f"✅ Заявка #{app_id} создана.\n"
                f"Ожидайте одобрения студента."
            )
        else:
            await update.message.reply_text("❌ У вас нет доступа к этой заявке.")

    except (ValueError, IndexError, InternshipApplication.DoesNotExist):
        await update.message.reply_text("❌ Некорректная ссылка на заявку.")
        logger.error(f"Invalid application link: {param}")


async def handle_chat_link(update: Update, context: CallbackContext, param: str):
    """Обрабатывает присоединение к чату"""
    try:
        app_id = int(param.split('_')[1])
        context.args = [str(app_id)]
        await join_chat(update, context)
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Некорректная ссылка на чат.")
        logger.error(f"Invalid chat link: {param}")


# ============================================================================
# КОМАНДА /REGISTER
# ============================================================================

async def register(update: Update, context: CallbackContext):
    """
    Привязывает Telegram к аккаунту пользователя

    Использование: /register example@email.com
    """
    logger.info(f"📝 /register from user {update.effective_user.id}")

    if not context.args:
        await update.message.reply_text(
            "📝 Укажите email:\n"
            "/register your@email.com"
        )
        return

    email = context.args[0].strip().lower()
    tg_user = update.effective_user
    chat = update.effective_chat

    User = get_user_model()

    try:
        # Ищем пользователя по email
        user = await sync_to_async(User.objects.get)(email=email)

        # Создаем или обновляем Telegram профиль
        await sync_to_async(TelegramProfile.objects.update_or_create)(
            user=user,
            defaults={
                'telegram_user_id': tg_user.id,
                'chat_id': chat.id,
                'username': tg_user.username or tg_user.first_name or ''
            }
        )

        # Обновляем данные студента
        await sync_to_async(Student.objects.filter(user=user).update)(
            telegram_user_id=tg_user.id,
            telegram_chat_id=chat.id
        )

        await update.message.reply_text(
            f"✅ Telegram успешно привязан к аккаунту!\n"
            f"📧 Email: {email}"
        )
        logger.info(f"✅ User {email} registered with TG {tg_user.id}")

    except User.DoesNotExist:
        await update.message.reply_text(
            f"❌ Пользователь с email {email} не найден.\n"
            f"Проверьте правильность email или зарегистрируйтесь на платформе."
        )
        logger.warning(f"⚠️ User not found: {email}")


# ============================================================================
# КОМАНДА /ACCEPT
# ============================================================================

async def accept(update: Update, context: CallbackContext):
    """
    Принимает заявку
    Может использоваться студентом или куратором

    Использование: /accept 123
    """
    logger.info(f"✅ /accept from user {update.effective_user.id}, args: {context.args}")

    if not context.args:
        await update.message.reply_text("📝 Укажите ID заявки:\n/accept 123")
        return

    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID заявки.")
        return

    tg_user_id = update.effective_user.id

    try:
        # Получаем заявку
        application = await sync_to_async(
            lambda: InternshipApplication.objects.select_related(
                'student', 'employer'
            ).get(id=app_id)
        )()

        # Проверяем права
        is_student = application.student.telegram_user_id == tg_user_id
        is_moderator = await sync_to_async(
            lambda: TelegramProfile.objects.filter(
                telegram_user_id=tg_user_id,
                is_moderator=True
            ).exists()
        )()

        if not is_student and not is_moderator:
            await update.message.reply_text("❌ У вас нет прав для принятия этой заявки.")
            return

        # Обновляем статус
        if is_student:
            application.student_response = 'accepted'
            logger.info(f"✅ Student accepted application #{app_id}")

        if is_moderator:
            application.moderator_response = 'accepted'
            logger.info(f"✅ Moderator accepted application #{app_id}")

        await sync_to_async(application.save)()

        # Проверяем, нужно ли одобрение куратора
        if requires_curator_approval(application.student):
            if application.moderator_response != 'accepted':
                await update.message.reply_text(
                    f"⏳ Заявка #{app_id} принята.\n"
                    f"Ожидается одобрение куратора (студент младше 18 лет)."
                )
                return

        # Если все одобрения получены - создаем чат
        if application.student_response == 'accepted':
            if not requires_curator_approval(application.student) or \
                    application.moderator_response == 'accepted':

                chat_id = await sync_to_async(
                    lambda: create_communication_chat(application)
                )()

                if chat_id:
                    await update.message.reply_text(
                        f"✅ Заявка #{app_id} принята!\n"
                        f"💬 Чат создан. Можете начать общение."
                    )
                else:
                    await update.message.reply_text(
                        f"✅ Заявка #{app_id} принята, но возникла ошибка при создании чата."
                    )
                return

        await update.message.reply_text(
            f"✅ Заявка #{app_id} принята.\n"
            f"Ожидаем подтверждения от других участников."
        )

    except InternshipApplication.DoesNotExist:
        await update.message.reply_text(f"❌ Заявка #{app_id} не найдена.")
        logger.error(f"Application #{app_id} not found")


# ============================================================================
# КОМАНДА /REJECT
# ============================================================================

async def reject(update: Update, context: CallbackContext):
    """
    Отклоняет заявку

    Использование: /reject 123
    """
    logger.info(f"❌ /reject from user {update.effective_user.id}, args: {context.args}")

    if not context.args:
        await update.message.reply_text("📝 Укажите ID заявки:\n/reject 123")
        return

    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID заявки.")
        return

    tg_user_id = update.effective_user.id

    try:
        # Получаем заявку
        application = await sync_to_async(
            lambda: InternshipApplication.objects.select_related(
                'student', 'employer'
            ).get(id=app_id)
        )()

        # Проверяем права
        is_student = application.student.telegram_user_id == tg_user_id
        is_moderator = await sync_to_async(
            lambda: TelegramProfile.objects.filter(
                telegram_user_id=tg_user_id,
                is_moderator=True
            ).exists()
        )()

        if not is_student and not is_moderator:
            await update.message.reply_text("❌ У вас нет прав для отклонения этой заявки.")
            return

        # Обновляем статус
        if is_student:
            application.student_response = 'rejected'
        if is_moderator:
            application.moderator_response = 'rejected'

        application.status = 'rejected'
        await sync_to_async(application.save)()

        await update.message.reply_text(f"❌ Заявка #{app_id} отклонена.")
        logger.info(f"❌ Application #{app_id} rejected by user {tg_user_id}")

    except InternshipApplication.DoesNotExist:
        await update.message.reply_text(f"❌ Заявка #{app_id} не найдена.")


# ============================================================================
# КОМАНДА /JOIN_CHAT
# ============================================================================

async def join_chat(update: Update, context: CallbackContext):
    """
    Присоединяет работодателя к чату

    Использование: /join_chat 123
    """
    logger.info(f"💬 /join_chat from user {update.effective_user.id}")

    if not context.args:
        await update.message.reply_text("📝 Укажите ID заявки:\n/join_chat 123")
        return

    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID заявки.")
        return

    tg_user = update.effective_user
    chat = update.effective_chat

    try:
        # Получаем заявку
        application = await sync_to_async(
            lambda: InternshipApplication.objects.select_related(
                'student', 'employer'
            ).get(id=app_id)
        )()

        # Проверяем статус заявки
        if application.status != 'accepted':
            await update.message.reply_text("❌ Заявка еще не принята.")
            return

        # Проверяем наличие сессии
        if not hasattr(application, 'communication_session'):
            await update.message.reply_text("❌ Чат для этой заявки еще не создан.")
            return

        session = application.communication_session

        # Создаем профиль работодателя
        employer_profile, created = await sync_to_async(
            lambda: TelegramProfile.objects.get_or_create(
                telegram_user_id=tg_user.id,
                defaults={
                    'chat_id': chat.id,
                    'username': tg_user.username or tg_user.first_name or 'Employer'
                }
            )
        )()

        # Добавляем в участники
        participant, created = await sync_to_async(
            lambda: ChatParticipant.objects.get_or_create(
                session=session,
                profile=employer_profile,
                defaults={'role': 'employer'}
            )
        )()

        if created:
            # Уведомляем всех участников
            welcome_text = f"👨💼 Работодатель {tg_user.first_name} присоединился к чату!"

            all_participants = await sync_to_async(
                lambda: list(session.participants.select_related('profile').all())
            )()

            for p in all_participants:
                if p.profile.telegram_user_id != tg_user.id:
                    send_telegram_message(p.profile.chat_id, welcome_text)

            await update.message.reply_text(
                f"✅ Вы присоединились к чату для заявки #{app_id}\n"
                f"👨🎓 Студент: {application.student.full_name}\n"
                f"💬 Можете начать общение."
            )
            logger.info(f"✅ Employer {tg_user.id} joined session #{session.id}")
        else:
            await update.message.reply_text("ℹ️ Вы уже в этом чате.")

    except InternshipApplication.DoesNotExist:
        await update.message.reply_text(f"❌ Заявка #{app_id} не найдена.")


# ============================================================================
# КОМАНДА /CLOSE_SESSION
# ============================================================================

async def close_session(update: Update, context: CallbackContext):
    """
    Завершает сессию общения

    Использование: /close_session 123
    """
    logger.info(f"🔚 /close_session from user {update.effective_user.id}")

    if not context.args:
        await update.message.reply_text("📝 Укажите ID заявки:\n/close_session 123")
        return

    try:
        app_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID заявки.")
        return

    tg_user_id = update.effective_user.id

    try:
        # Получаем заявку и сессию
        application = await sync_to_async(
            lambda: InternshipApplication.objects.get(id=app_id)
        )()

        session = await sync_to_async(
            lambda: application.communication_session
        )()

        # Проверяем права
        is_participant = await sync_to_async(
            lambda: session.participants.filter(
                profile__telegram_user_id=tg_user_id
            ).exists()
        )()

        if not is_participant:
            await update.message.reply_text("❌ Вы не участник этого чата.")
            return

        # Завершаем сессию
        session.session_status = 'completed'
        await sync_to_async(session.save)()

        application.status = 'completed'
        await sync_to_async(application.save)()

        # Уведомляем всех участников
        completion_text = f"✅ Чат для заявки #{app_id} завершён."

        participants = await sync_to_async(
            lambda: list(session.participants.select_related('profile').all())
        )()

        for participant in participants:
            send_telegram_message(participant.profile.chat_id, completion_text)

        await update.message.reply_text(f"✅ Сессия для заявки #{app_id} завершена.")
        logger.info(f"✅ Session #{session.id} completed by user {tg_user_id}")

    except (InternshipApplication.DoesNotExist, CommunicationSession.DoesNotExist):
        await update.message.reply_text(f"❌ Заявка или сессия не найдена.")


# ============================================================================
# ОБРАБОТЧИК СООБЩЕНИЙ В ЧАТЕ
# ============================================================================

async def handle_chat_message(update: Update, context: CallbackContext):
    """
    Пересылает сообщения между участниками чата
    """
    message = update.message
    tg_user_id = update.effective_user.id
    text = message.text

    # Пропускаем команды
    if text.startswith('/'):
        return

    logger.info(f"💬 New message from user {tg_user_id}: {text[:50]}...")

    try:
        # Находим активные сессии пользователя
        sessions = await sync_to_async(
            lambda: list(
                CommunicationSession.objects.filter(
                    participants__profile__telegram_user_id=tg_user_id,
                    session_status='active'
                ).select_related('application').prefetch_related(
                    'participants__profile'
                )
            )
        )()

        if not sessions:
            logger.info(f"No active sessions for user {tg_user_id}")
            return

        session = sessions[0]

        # Получаем отправителя
        sender = await sync_to_async(
            lambda: session.participants.select_related('profile').filter(
                profile__telegram_user_id=tg_user_id
            ).first()
        )()

        if not sender:
            await update.message.reply_text("❌ Вы не участник этого чата.")
            return

        # Получаем других участников
        participants = await sync_to_async(
            lambda: list(
                session.participants.select_related('profile').exclude(
                    profile__telegram_user_id=tg_user_id
                )
            )
        )()

        if not participants:
            await update.message.reply_text("ℹ️ В чате нет других участников.")
            return

        # Формируем текст сообщения
        role_icons = {
            'student': '👨🎓',
            'employer': '👨💼',
            'curator': '👨🏫'
        }
        icon = role_icons.get(sender.role, '👤')
        sender_name = sender.profile.username or f"User_{tg_user_id}"

        forwarded_text = f"{icon} {sender_name}:\n{text}"

        # Пересылаем всем участникам
        sent_count = 0
        for participant in participants:
            if send_telegram_message(participant.profile.chat_id, forwarded_text):
                sent_count += 1

        # Обновляем статистику сессии
        session.message_count += 1
        session.last_activity = timezone.now()
        await sync_to_async(session.save)()

        logger.info(f"✅ Message forwarded to {sent_count} participants")

    except Exception as e:
        logger.error(f"❌ Error handling chat message: {e}")


