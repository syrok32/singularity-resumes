import django_filters
from django.db import models
from django.utils import timezone
from datetime import date
from .models import Student, Specialty, Skill


class StudentFilter(django_filters.FilterSet):
    # Фильтр по курсу (множественный выбор)
    course = django_filters.MultipleChoiceFilter(
        choices=[(str(i), str(i)) for i in range(1, 5)],
        field_name='course',
        lookup_expr='in'
    )
    
    # Фильтр по специальности (множественный выбор)
    specialty = django_filters.ModelMultipleChoiceFilter(
        queryset=Specialty.objects.all(),
        field_name='specialty',
        to_field_name='id'
    )
    
    # Фильтр по специальности по имени
    specialty_name = django_filters.ModelMultipleChoiceFilter(
        queryset=Specialty.objects.all(),
        field_name='specialty__name',
        to_field_name='name'
    )
    
    # Фильтр по навыкам (множественный выбор)
    skills = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        field_name='skills',
        to_field_name='id'
    )
    
    # Фильтр по навыкам по имени
    skills_name = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        field_name='skills__name',
        to_field_name='name'
    )
    
    # Фильтр по городу (множественный выбор)
    cities = django_filters.MultipleChoiceFilter(
        choices=[],  # Будем заполнять динамически
        field_name='city',
        lookup_expr='in'
    )
    
    # Фильтр по возрасту (больше 18 лет)
    over_18 = django_filters.BooleanFilter(
        method='filter_over_18',
        label='Старше 18 лет'
    )
    
    # Поиск по имени
    search = django_filters.CharFilter(
        method='filter_search',
        label='Поиск'
    )
    
    # Фильтр по наличию опыта работы
    has_experience = django_filters.BooleanFilter(
        method='filter_has_experience',
        label='Есть опыт работы'
    )
    
    # Фильтр по наличию портфолио
    has_portfolio = django_filters.BooleanFilter(
        method='filter_has_portfolio',
        label='Есть портфолио'
    )

    class Meta:
        model = Student
        fields = {
            'course': ['exact', 'in'],
            'is_active': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически заполняем выбор городов
        cities = Student.objects.values_list('city', flat=True).distinct().order_by('city')
        city_choices = [(city, city) for city in cities if city]
        self.filters['cities'].extra['choices'] = city_choices
        
        # Фильтрация навыков по выбранной специальности
        self._update_skills_queryset()
    
    def _update_skills_queryset(self):
        """Обновляет queryset навыков в зависимости от выбранной специальности"""
        specialty_ids = self.data.getlist('specialty') if self.data else []
        if specialty_ids:
            # Фильтруем навыки по тем, которые есть у студентов выбранных специальностей
            skills_queryset = Skill.objects.filter(
                student__specialty__id__in=specialty_ids
            ).distinct()
            self.filters['skills'].queryset = skills_queryset
            self.filters['skills_name'].queryset = skills_queryset

    def filter_search(self, queryset, name, value):
        """Поиск по имени, биографии, городу"""
        if value:
            return queryset.filter(
                models.Q(full_name__icontains=value) |
                models.Q(bio__icontains=value) |
                models.Q(city__icontains=value) |
                models.Q(skills__name__icontains=value) |
                models.Q(specialty__name__icontains=value)
            ).distinct()
        return queryset

    def filter_has_experience(self, queryset, name, value):
        """Фильтр по наличию опыта работы"""
        if value is True:
            return queryset.filter(work_experiences__isnull=False).distinct()
        elif value is False:
            return queryset.filter(work_experiences__isnull=True).distinct()
        return queryset

    def filter_has_portfolio(self, queryset, name, value):
        """Фильтр по наличию портфолио"""
        if value is True:
            return queryset.filter(portfolios__isnull=False).distinct()
        elif value is False:
            return queryset.filter(portfolios__isnull=True).distinct()
        return queryset
    
    def filter_over_18(self, queryset, name, value):
        """Фильтр по возрасту больше 18 лет"""
        if value is True:
            # Вычисляем дату 18 лет назад от сегодняшнего дня
            eighteen_years_ago = date.today().replace(year=date.today().year - 18)
            return queryset.filter(birth_date__lt=eighteen_years_ago)
        elif value is False:
            # Младше 18 лет
            eighteen_years_ago = date.today().replace(year=date.today().year - 18)
            return queryset.filter(birth_date__gte=eighteen_years_ago)
        return queryset