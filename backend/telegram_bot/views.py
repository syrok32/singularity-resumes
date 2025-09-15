from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from student.models import Student, InternshipApplication
from telegram_bot.services import send_application_notification


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_application(request):
    """Создаёт заявку на стажировку и отправляет уведомления в Telegram"""
    data = request.data or {}

    student_id = data.get('student_id')
    employer_name = (data.get('employer_name') or '').strip()
    message = (data.get('message') or '').strip()

    if not student_id or not employer_name or not message:
        return Response({'detail': 'student_id, employer_name и message — обязательны'}, status=400)

    student = Student.objects.filter(id=student_id, is_active=True).first()
    if not student:
        return Response({'detail': 'Студент не найден или неактивен'}, status=404)

    application = InternshipApplication.objects.create(
        student=student,
        employer_name=employer_name,
        message=message,
    )

    try:
        send_application_notification(application)
    except Exception:
        pass

    return Response({'id': application.id, 'status': application.status, 'student_id': student.id}, status=201)


