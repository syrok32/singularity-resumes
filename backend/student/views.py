from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
# from ..singularityResumes import settings
from .models import Student, Specialty, Skill
from .serializers import StudentProfileSerializer, StudentCardSerializer
from .filters import StudentFilter


class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.select_related('specialty', 'user').prefetch_related(
        'skills__category', 'educations__specialty', 'work_experiences', 'portfolios'
    ).filter(is_active=True)
    serializer_class = StudentProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StudentPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ['full_name', 'city', 'bio', 'skills__name', 'specialty__name']
    ordering_fields = ['full_name', 'course', 'city']
    ordering = ['full_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentCardSerializer
        return StudentProfileSerializer

    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Возвращает доступные опции для фильтров"""
        # Получаем все специальности
        specialties = Specialty.objects.all().values('id', 'name')

        # Получаем все навыки
        skills = Skill.objects.select_related('category').all().values(
            'id', 'name', 'category__name'
        )

        # Получаем все курсы
        courses = Student.objects.values_list('course', flat=True).distinct().order_by('course')

        # Получаем все города
        cities = Student.objects.values_list('city', flat=True).distinct().order_by('city')
        cities = [city for city in cities if city]  # Убираем пустые значения

        return Response({
            'specialties': list(specialties),
            'skills': list(skills),
            'courses': list(courses),
            'cities': cities
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Возвращает статистику студентов"""
        total_students = self.get_queryset().count()

        # Статистика по курсам
        course_stats = {}
        for course in range(1, 5):
            count = self.get_queryset().filter(course=str(course)).count()
            course_stats[f'course_{course}'] = count

        # Статистика по специальностям
        specialty_stats = []
        for specialty in Specialty.objects.all():
            count = self.get_queryset().filter(specialty=specialty).count()
            if count > 0:
                specialty_stats.append({
                    'name': specialty.name,
                    'count': count
                })

        # Топ навыков
        from django.db.models import Count
        top_skills = Skill.objects.annotate(
            student_count=Count('student', filter=models.Q(student__is_active=True))
        ).filter(student_count__gt=0).order_by('-student_count')[:10]

        top_skills_data = [
            {'name': skill.name, 'count': skill.student_count}
            for skill in top_skills
        ]

        return Response({
            'total_students': total_students,
            'course_stats': course_stats,
            'specialty_stats': specialty_stats,
            'top_skills': top_skills_data
        })

# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from telegram import Update
# from ..telegram_bot.bots import application
#
# @csrf_exempt
# def telegram_webhook(request, token):
#     if token == settings.TELEGRAM_BOT_TOKEN and request.method == 'POST':
#         update = Update.de_json(request.body.decode('utf-8'), application.bot)
#         application.process_update(update)
#         return HttpResponse(status=200)
#     return HttpResponse("Unauthorized", status=403)