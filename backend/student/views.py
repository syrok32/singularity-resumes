"""
Представления (ViewSets) для приложения student.
Оптимизированы для производительности и кеширования.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Student, Specialty, Skill
from .serializers import (
    StudentProfileSerializer,
    StudentCardSerializer,
    StudentListSerializer,
    FilterOptionsSerializer,
    StudentStatsSerializer
)
from .filters import StudentFilter


class StudentPagination(PageNumberPagination):
    """
    Кастомная пагинация для студентов.
    Позволяет фронтенду управлять размером страницы.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Расширенный ответ с метаинформацией."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        })


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для профилей студентов.

    Поддерживает:
    - Листинг студентов с фильтрацией, поиском и сортировкой
    - Детальный просмотр профиля студента
    - Получение топ-студентов для главной страницы
    - Фильтры и статистику

    Endpoints:
    - GET /api/students/profiles/ - список студентов
    - GET /api/students/profiles/{id}/ - детальный профиль
    - GET /api/students/profiles/top/ - топ студенты для главной
    - GET /api/students/profiles/filter_options/ - опции фильтров
    - GET /api/students/profiles/stats/ - статистика
    """

    permission_classes = [AllowAny]
    pagination_class = StudentPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentFilter

    # Поля для полнотекстового поиска
    search_fields = [
        'full_name',
        'bio',
        'city',
        'skills__name',
        'specialty__name'
    ]

    # Поля для сортировки
    ordering_fields = [
        'full_name',
        'course',
        'city',
        'created_at'
    ]
    ordering = ['-created_at']  # По умолчанию сортировка по дате создания

    def get_queryset(self):
        """
        Оптимизированный queryset с предзагрузкой связанных объектов.
        Предотвращает проблему N+1.
        """
        queryset = Student.objects.active()

        # Для списка используем оптимизацию карточек
        if self.action == 'list':
            return queryset.with_card_data()

        # Для детального просмотра загружаем полный профиль
        elif self.action == 'retrieve':
            return queryset.with_full_profile()

        # Для остальных действий базовая оптимизация
        return queryset.select_related('specialty', 'user')

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return StudentCardSerializer
        elif self.action == 'top':
            return StudentListSerializer
        return StudentProfileSerializer

    @swagger_auto_schema(
        operation_description="Получить список топ-студентов для главной страницы",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Количество студентов (по умолчанию 10)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: StudentListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))  # Кеш на 15 минут
    def top(self, request):
        """
        Возвращает топ-студентов для отображения на главной странице.

        Логика выбора:
        - Активные студенты
        - С заполненным профилем (био, навыки, специальность)
        - Сортировка по дате создания (новые)
        - Лимит по умолчанию: 10
        """
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Максимум 50

        # Получаем студентов с полным профилем
        students = (
            Student.objects.active()
            .with_card_data()
            .exclude(bio='')
            .exclude(specialty__isnull=True)
            .filter(skills__isnull=False)
            .distinct()
            .order_by('-created_at')[:limit]
        )

        serializer = self.get_serializer(students, many=True)
        return Response({
            'count': len(serializer.data),
            'students': serializer.data
        })

    @swagger_auto_schema(
        operation_description="Получить опции для фильтров (специальности, навыки, города, курсы)",
        responses={200: openapi.Response(
            description="Опции фильтров",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'specialties': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'skills': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'skills_by_category': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'courses': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'cities': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                }
            )
        )}
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 30))  # Кеш на 30 минут
    def filter_options(self, request):
        """
        Возвращает все доступные опции для фильтров.
        Кешируется на 30 минут.
        """
        from .api_views import get_filter_options_data
        data = get_filter_options_data()
        return Response(data)

