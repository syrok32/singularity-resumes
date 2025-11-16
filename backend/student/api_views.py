"""
API views для вспомогательных endpoint'ов.
Содержит бизнес-логику для фильтров и статистики.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Student, Specialty, Skill, SkillCategory


def get_filter_options_data():
    """
    Получает данные для опций фильтров.
    Вынесено в отдельную функцию для удобства кеширования.
    """
    cache_key = 'filter_options_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    # Специальности
    specialties = list(
        Specialty.objects.all()
        .values('id', 'name')
        .order_by('name')
    )

    # Навыки с категориями
    skills = list(
        Skill.objects.select_related('category')
        .values('id', 'name', 'category__id', 'category__name')
        .order_by('category__name', 'name')
    )

    # Группируем навыки по категориям для удобства фронтенда
    skills_by_category = {}
    for skill in skills:
        category_name = skill['category__name'] or 'Без категории'
        if category_name not in skills_by_category:
            skills_by_category[category_name] = []
        skills_by_category[category_name].append({
            'id': skill['id'],
            'name': skill['name']
        })

    # Курсы
    courses = [
        {'value': str(i), 'label': f'{i} курс'}
        for i in range(1, 5)
    ]

    # Города (только те, где есть активные студенты)
    cities = list(
        Student.objects.active()
        .exclude(city__isnull=True)
        .exclude(city='')
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    data = {
        'specialties': specialties,
        'skills': skills,
        'skills_by_category': skills_by_category,
        'courses': courses,
        'cities': cities
    }

    # Кешируем на 30 минут
    cache.set(cache_key, data, 60 * 30)

    return data


def get_student_stats_data():
    """
    Получает статистику по студентам.
    Вынесено в отдельную функцию для удобства кеширования.
    """
    cache_key = 'student_stats_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    active_students = Student.objects.active()
    total_students = active_students.count()

    # Защита от деления на ноль
    if total_students == 0:
        return {
            'total_students': 0,
            'course_stats': [],
            'specialty_stats': [],
            'top_skills': [],
            'city_stats': []
        }

    # Статистика по курсам
    course_stats = []
    for course in range(1, 5):
        count = active_students.filter(course=str(course)).count()
        course_stats.append({
            'course': str(course),
            'count': count,
            'percentage': round((count / total_students * 100), 1)
        })

    # Статистика по специальностям (топ-10)
    specialty_stats = []
    specialties_data = (
        active_students
        .exclude(specialty__isnull=True)
        .values('specialty__id', 'specialty__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    for item in specialties_data:
        specialty_stats.append({
            'id': item['specialty__id'],
            'name': item['specialty__name'],
            'count': item['count'],
            'percentage': round((item['count'] / total_students * 100), 1)
        })

    # Топ-10 навыков
    top_skills = []
    skills_data = (
        Skill.objects
        .filter(students__is_active=True)
        .select_related('category')
        .annotate(student_count=Count('students', distinct=True))
        .order_by('-student_count')[:10]
    )

    for skill in skills_data:
        top_skills.append({
            'id': skill.id,
            'name': skill.name,
            'count': skill.student_count,
            'category': skill.category.name if skill.category else 'Без категории'
        })

    # Статистика по городам (топ-10)
    city_stats = []
    cities_data = (
        active_students
        .exclude(city__isnull=True)
        .exclude(city='')
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    for item in cities_data:
        city_stats.append({
            'name': item['city'],
            'count': item['count'],
            'percentage': round((item['count'] / total_students * 100), 1)
        })

    data = {
        'total_students': total_students,
        'course_stats': course_stats,
        'specialty_stats': specialty_stats,
        'top_skills': top_skills,
        'city_stats': city_stats
    }

    # Кешируем на 15 минут
    cache.set(cache_key, data, 60 * 15)

    return data


@swagger_auto_schema(
    method='get',
    operation_description='Получить опции для фильтров',
    responses={
        200: openapi.Response(
            description='Успешный ответ',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'specialties': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    ),
                    'skills': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'skills_by_category': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'courses': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'cities': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def filter_options(request):
    """
    Возвращает все доступные опции для фильтров.

    Response:
    - specialties: список специальностей с id и названием
    - skills: список всех навыков с категориями
    - skills_by_category: навыки, сгруппированные по категориям
    - courses: список доступных курсов
    - cities: список городов, где есть студенты
    """
    data = get_filter_options_data()
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_description='Получить статистику по студентам',
    responses={
        200: openapi.Response(
            description='Успешный ответ',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_students': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'course_stats': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'specialty_stats': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'top_skills': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'city_stats': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def student_stats(request):
    """
    Возвращает статистику по студентам.

    Response:
    - total_students: общее количество активных студентов
    - course_stats: статистика по курсам (количество и процент)
    - specialty_stats: топ-10 специальностей
    - top_skills: топ-10 навыков
    - city_stats: топ-10 городов
    """
    data = get_student_stats_data()
    return Response(data)


# Дополнительные helper-функции для инвалидации кеша

def invalidate_filter_options_cache():
    """
    Инвалидирует кеш опций фильтров.
    Вызывается при изменении справочников (навыки, специальности).
    """
    cache.delete('filter_options_data')




def invalidate_all_caches():
    """Инвалидирует все кеши приложения student."""
    invalidate_filter_options_cache()

