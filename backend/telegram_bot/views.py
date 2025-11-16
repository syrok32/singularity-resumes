# telegram_bot/views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from student.models import Student, InternshipApplication, Employer
from .services import (
    send_application_notification,
    send_employer_registration_email  # Новая функция
)
import logging
import uuid

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_application(request):
    """
    Production-grade создание заявки на стажировку

    POST /api/v1/applications/

    Request body:
    {
        "student_id": 1,
        "employer_name": "Иван Иванов",
        "company": "ООО 'Компания'",
        "employer_telegram": "@username", (optional)
        "employer_email": "ivan@example.com" (optional)
    }

    Response:
    {
        "id": 123,
        "status": "pending",
        "employer_bot_link": "t.me/bot?start=employer_123_token123",
        "tracking_token": "abc123def456",
        "message": "Заявка создана. Работодатель получит email с доступом к боту."
    }
    """

    data = request.data
    logger.info(f"📝 Создание заявки: {data}")

    # Валидация обязательных полей (по вашей форме)
    student_id = data.get('student_id')
    employer_name = data.get('employer_name')
    company = data.get('company')
    employer_telegram = data.get('employer_telegram', '')
    employer_email = data.get('employer_email', '')

    if not all([student_id, employer_name, company]):
        logger.warning(f"❌ Отсутствуют обязательные поля: {data}")
        return Response({
            'error': 'Требуются поля: student_id, employer_name, company'
        }, status=400)

    # Проверяем существование студента
    try:
        student = Student.objects.get(id=student_id, is_active=True)
        if not student.telegram_chat_id:
            logger.warning(f"⚠️ Студент {student_id} не зарегистрирован в Telegram")
            return Response({
                'error': 'Студент не зарегистрирован в Telegram боте',
                'student_email': student.user.email  # Для отладки
            }, status=412)  # Precondition Failed
    except Student.DoesNotExist:
        logger.error(f"❌ Студент {student_id} не найден")
        return Response({
            'error': 'Студент не найден или неактивен'
        }, status=404)

    # Создаем или находим работодателя (без дубликатов)
    employer, created = Employer.objects.get_or_create(
        name=f"{employer_name} ({company})",  # Комбинируем имя и компанию
        defaults={
            'email': employer_email or '',
            'telegram_id': employer_telegram.replace('@', '') if employer_telegram else ''
        }
    )

    # Создаем заявку с уникальным tracking token
    tracking_token = str(uuid.uuid4())[:12]  # Безопасный токен для верификации
    application = InternshipApplication.objects.create(
        student=student,
        employer=employer,
        message=f"Приглашение от {company}",
        company_name=company,
        telegram_user_id=employer_telegram,
        employer_email=employer_email,
        tracking_token=tracking_token,  # Для безопасности
        sla_deadline=timezone.now() + timedelta(hours=12),
        status='pending'
    )

    logger.info(f"✅ Заявка создана: ID={application.id}, Employer={employer_name}")

    # Генерируем secure deep-link для работодателя
    employer_bot_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=employer_{application.id}_{tracking_token}"

    # ✅ АВТОМАТИЗАЦИЯ: Отправляем уведомления
    send_application_notification(application)

    # Отправляем персонализированный email работодателю
    if employer_email:
        send_employer_registration_email(
            application,
            employer_email,
            employer_name,
            employer_bot_link,
            student.full_name
        )
        logger.info(f"📧 Email отправлен на {employer_email}")
    else:
        logger.info(f"⚠️ Email не указан, работодатель получит только ссылку")

    # Отправляем уведомление куратору (если студент <18)
    if student.age and student.age < 18:
        logger.info(f"⚠️ Студент {student.full_name} <18 лет - уведомляем кураторов")
        from .services import notify_curators_about_minor
        notify_curators_about_minor(application)

    # Запускаем SLA-таймер (Celery задача)
    from .tasks import start_sla_timer
    start_sla_timer.delay(application.id)

    logger.info(f"🚀 Заявка #{application.id} запущена в production pipeline")

    return Response({
        'id': application.id,
        'status': 'pending',
        'employer_bot_link': employer_bot_link,
        'tracking_token': tracking_token,
        'message': 'Заявка создана и запущена в автоматизированный процесс. Работодатель получит email с доступом к боту.',
        'next_steps': [
            'Студент уведомлен в Telegram',
            'Работодателю отправлен email с deep-link',
            'SLA таймер запущен (12 часов)',
            'Кураторы уведомлены (если студент <18)'
        ]
    }, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def application_status(request, id):
    """
    Проверка статуса заявки (для фронтенда)

    GET /api/v1/applications/{id}/status/
    """
    try:
        application = InternshipApplication.objects.select_related(
            'student', 'employer'
        ).get(id=id)

        return Response({
            'id': application.id,
            'status': application.status,
            'student_name': application.student.full_name,
            'employer_name': application.employer.name,
            'company': application.company_name,
            'created_at': application.created_at.isoformat(),
            'sla_remaining': (
                                         application.sla_deadline - timezone.now()).seconds // 3600 if application.sla_deadline else None,
            'chat_created': application.chat_created
        })
    except InternshipApplication.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
