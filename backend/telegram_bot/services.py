"""
Сервисы Telegram-бота
=====================
Содержит всю бизнес-логику:
- Отправка сообщений в Telegram
- Уведомления участников
- Создание чатов и сессий
- Проверка возраста и эскалация к кураторам
"""

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from student.models import InternshipApplication
from telegram_bot.models import TelegramProfile, CommunicationSession, ChatParticipant
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ТЕЛЕГРАМ API
# ============================================================================

def send_telegram_message(
        chat_id: int,
        text: str,
        reply_markup: dict = None,
        parse_mode: str = None
) -> bool:
    """
    Отправляет сообщение в Telegram через Bot API

    Args:
        chat_id: ID чата получателя
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        parse_mode: Форматирование (Markdown, HTML)

    Returns:
        bool: True если отправлено успешно
    """
    try:
        api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': str(chat_id),
            'text': text
        }

        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup, ensure_ascii=False)

        if parse_mode:
            data['parse_mode'] = parse_mode

        payload = urlencode(data).encode('utf-8')
        req = Request(api_url, data=payload)

        with urlopen(req, timeout=10) as response:
            logger.info(f"✅ Message sent to {chat_id}")
            return True

    except Exception as e:
        logger.error(f"❌ Error sending message to {chat_id}: {e}")
        return False


# ============================================================================
# ПРОВЕРКИ И ВАЛИДАЦИЯ
# ============================================================================

def requires_curator_approval(student) -> bool:
    """
    Проверяет, требуется ли одобрение куратора
    (для студентов младше 18 лет)

    Args:
        student: Объект Student

    Returns:
        bool: True если требуется куратор
    """
    if not student.age:
        return False
    return student.age < 18


# ============================================================================
# УВЕДОМЛЕНИЯ
# ============================================================================


def send_application_notification(application: InternshipApplication):
    """
    Отправляет уведомление о новой заявке БЕЗ сообщения
    """
    # Формируем текст уведомления
    notification_text = (
        f"📩 Новая заявка #{application.id}\n\n"
        f"👤 От: {application.employer.name}\n"
        f"🏢 Компания: {application.company_name}\n"
        f"📧 Email: {application.employer.email}\n"
        f"📱 Telegram: @{application.telegram_user_id}\n\n"
        f"✅ Принять: /accept {application.id}\n"
        f"❌ Отклонить: /reject {application.id}"
    )

    # Отправляем студенту
    if application.student.telegram_chat_id:
        send_telegram_message(
            application.student.telegram_chat_id,
            notification_text
        )
        logger.info(f"📤 Notification sent to student #{application.student.id}")

    # Отправляем кураторам (если студент < 18)
    if requires_curator_approval(application.student):
        curator_text = (
            f"⚠️ Требуется одобрение куратора\n\n"
            f"{notification_text}\n\n"
            f"Студент: {application.student.full_name} ({application.student.age} лет)"
        )

        for curator in TelegramProfile.objects.filter(is_moderator=True):
            send_telegram_message(curator.chat_id, curator_text)
            logger.info(f"📤 Curator notification sent to #{curator.id}")

def send_sla_reminder(application: InternshipApplication):
    """
    Отправляет напоминание о истекающем SLA

    Args:
        application: Объект InternshipApplication
    """
    reminder_text = (
        f"⏰ Внимание! Истекает SLA для заявки #{application.id}\n\n"
        f"Осталось времени до дедлайна.\n"
        f"Пожалуйста, ответьте на заявку."
    )

    # Студенту
    if application.student.telegram_chat_id:
        send_telegram_message(application.student.telegram_chat_id, reminder_text)

    # Кураторам
    for curator in TelegramProfile.objects.filter(is_moderator=True):
        send_telegram_message(curator.chat_id, reminder_text)

    # Отмечаем, что напоминание отправлено
    application.reminder_sent = True
    application.save()

    logger.info(f"⏰ SLA reminder sent for application #{application.id}")


# ============================================================================
# СОЗДАНИЕ ЧАТОВ
# ============================================================================

def create_communication_chat(application: InternshipApplication) -> int:
    """
    Создает сессию чата для заявки
    Добавляет всех участников: студент, куратор, работодатель

    Args:
        application: Объект InternshipApplication

    Returns:
        int: chat_id созданной сессии или None
    """
    try:
        # Получаем профиль студента
        student_profile = TelegramProfile.objects.filter(
            user=application.student.user
        ).first()

        if not student_profile:
            logger.warning(f"⚠️ Student profile not found for application #{application.id}")
            return None

        # Создаем сессию
        session = CommunicationSession.objects.create(
            application=application,
            chat_id=student_profile.chat_id
        )

        # Добавляем студента
        ChatParticipant.objects.create(
            session=session,
            profile=student_profile,
            role='student'
        )

        # Добавляем кураторов (если студент < 18 или по умолчанию)
        if requires_curator_approval(application.student):
            for curator in TelegramProfile.objects.filter(is_moderator=True):
                ChatParticipant.objects.create(
                    session=session,
                    profile=curator,
                    role='curator'
                )

        # Добавляем работодателя (если есть telegram_id)
        if application.employer.telegram_id:
            employer_profile, _ = TelegramProfile.objects.get_or_create(
                telegram_user_id=application.employer.telegram_id,
                defaults={
                    'chat_id': application.employer.telegram_id,
                    'username': application.employer.name
                }
            )
            ChatParticipant.objects.create(
                session=session,
                profile=employer_profile,
                role='employer'
            )

        # Обновляем статус заявки
        application.status = 'accepted'
        application.save()

        # Уведомляем всех участников
        welcome_text = (
            f"✅ Чат для заявки #{application.id} создан!\n\n"
            f"👨🎓 Студент: {application.student.full_name}\n"
            f"👨💼 Работодатель: {application.employer.name}\n\n"
            f"💬 Теперь вы можете общаться в этом чате."
        )

        for participant in session.participants.all():
            send_telegram_message(participant.profile.chat_id, welcome_text)

        logger.info(f"✅ Chat created for application #{application.id}, session #{session.id}")
        return session.chat_id

    except Exception as e:
        logger.error(f"❌ Error creating chat for application #{application.id}: {e}")
        return None


# ============================================================================
# EMAIL УВЕДОМЛЕНИЯ
# ============================================================================

# telegram_bot/services.py (добавьте в конец файла)

def send_employer_registration_email(application, employer_email, employer_name, bot_link, student_name):
    """
    Production-grade email для первого входа работодателя в бот

    Отправляет персонализированную инструкцию с deep-link
    """
    try:
        subject = f"🎯 Заявка #{application.id} отправлена - доступ к Telegram боту"

        # Production-ready HTML email
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Доступ к Telegram боту - Resume Student</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎯 Resume Student</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Платформа для стажировок</p>
            </div>

            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-top: 0; font-size: 24px; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Заявка #{application.id} отправлена</h2>

                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">📋 Детали заявки:</h3>
                    <p><strong>Студент:</strong> {student_name}</p>
                    <p><strong>Ваша компания:</strong> {application.company_name}</p>
                    <p><strong>Ваш email:</strong> {employer_email}</p>
                    <p><strong>Дата создания:</strong> {application.created_at.strftime('%d.%m.%Y %H:%M')}</p>
                    <p><strong>SLA дедлайн:</strong> {application.sla_deadline.strftime('%d.%m.%Y %H:%M')} (12 часов на ответ)</p>
                </div>

                <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3 style="margin-top: 0; color: #155724;">✅ Что происходит дальше:</h3>
                    <ol style="color: #155724;">
                        <li>Студент получил уведомление в Telegram</li>
                        <li>У студента 12 часов на принятие/отклонение заявки</li>
                        <li>Вы получите уведомление, когда студент ответит</li>
                        <li>После принятия заявки создастся чат для общения</li>
                    </ol>
                </div>

                <div style="text-align: center; margin: 30px 0; padding: 20px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid #667eea;">
                    <h3 style="margin-top: 0; color: #0c5460;">📱 Как начать работу с ботом:</h3>
                    <p style="font-size: 16px; margin: 15px 0;"><strong>1. Откройте Telegram</strong></p>
                    <p style="font-size: 16px; margin: 15px 0;"><strong>2. Перейдите по этой ссылке:</strong></p>

                    <a href="{bot_link}" 
                       style="display: inline-block; 
                              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold; 
                              font-size: 16px; 
                              margin: 20px 0; 
                              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                       🚀 Перейти в Telegram бот
                    </a>

                    <p style="font-size: 14px; color: #666; margin-top: 20px;">
                        <em>Ссылка действительна 7 дней. После перехода вы сможете получать уведомления 
                        и общаться со студентом в защищенном чате.</em>
                    </p>
                </div>

                <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>⚠️ Важно:</strong> Не делитесь этой ссылкой с другими. 
                        Она привязана к вашей заявке и содержит уникальный токен безопасности.
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
                    <p style="color: #666; font-size: 14px; margin: 0;">
                        С уважением,<br>
                        <strong>Команда Resume Student</strong><br><br>
                        <a href="https://t.me/YOUR_TELEGRAM_BOT" style="color: #667eea;">@YourBotUsername</a> | 
                        <a href="mailto:support@example.com" style="color: #667eea;">support@example.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        send_mail(
            subject,
            f"Заявка #{application.id} отправлена студенту {student_name}. Перейдите в Telegram бот: {bot_link}",
            settings.DEFAULT_FROM_EMAIL,
            [employer_email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"📧 Production email отправлен: {employer_email} → заявка #{application.id}")

    except Exception as e:
        logger.error(f"❌ Ошибка email: {e}", exc_info=True)
        # Не прерываем pipeline - email optional
