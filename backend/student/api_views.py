from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Specialty, Skill, SkillCategory, InternshipApplication
from telegram_bot.services import send_application_notification


@api_view(['GET'])
@permission_classes([AllowAny])
def filter_options(request):
    """Возвращает все доступные опции для фильтров"""
    
    # Специальности
    specialties = list(Specialty.objects.all().values('id', 'name'))
    
    # Навыки с категориями
    skills = list(Skill.objects.select_related('category').values(
        'id', 'name', 'category__id', 'category__name'
    ))
    
    # Группируем навыки по категориям
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
        {'value': '1', 'label': '1 курс'},
        {'value': '2', 'label': '2 курс'},
        {'value': '3', 'label': '3 курс'},
        {'value': '4', 'label': '4 курс'},
    ]
    
    # Города
    cities = list(Student.objects.exclude(city__isnull=True).exclude(city='')
                 .values_list('city', flat=True).distinct().order_by('city'))
    
    return Response({
        'specialties': specialties,
        'skills': skills,
        'skills_by_category': skills_by_category,
        'courses': courses,
        'cities': cities
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def student_stats(request):
    """Возвращает статистику по студентам"""
    
    active_students = Student.objects.filter(is_active=True)
    total_students = active_students.count()
    
    # Статистика по курсам
    course_stats = []
    for course in ['1', '2', '3', '4']:
        count = active_students.filter(course=course).count()
        course_stats.append({
            'course': course,
            'count': count,
            'percentage': round((count / total_students * 100) if total_students > 0 else 0, 1)
        })
    
    # Статистика по специальностям
    specialty_stats = []
    specialties_data = active_students.values('specialty__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in specialties_data:
        if item['specialty__name']:
            specialty_stats.append({
                'name': item['specialty__name'],
                'count': item['count'],
                'percentage': round((item['count'] / total_students * 100) if total_students > 0 else 0, 1)
            })
    
    # Топ навыков - упрощенная версия
    top_skills_data = []
    skills_with_students = Skill.objects.filter(student__is_active=True).annotate(
        student_count=Count('student', distinct=True)
    ).order_by('-student_count')[:10]
    
    for skill in skills_with_students:
        top_skills_data.append({
            'name': skill.name,
            'count': skill.student_count,
            'category': skill.category.name if skill.category else 'Без категории'
        })
    
    # Статистика по городам
    city_stats = []
    cities_data = active_students.exclude(city__isnull=True).exclude(city='').values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for item in cities_data:
        city_stats.append({
            'name': item['city'],
            'count': item['count']
        })
    
    return Response({
        'total_students': total_students,
        'course_stats': course_stats,
        'specialty_stats': specialty_stats,
        'top_skills': top_skills_data,
        'city_stats': city_stats
    })


