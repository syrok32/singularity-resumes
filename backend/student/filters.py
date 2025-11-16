"""
Фильтры для приложения student.
Оптимизированы для производительности и расширяемости.
"""

import django_filters
from django.db.models import Q, Exists, OuterRef
from datetime import date, timedelta
from .models import Student, Specialty, Skill


class StudentFilter(django_filters.FilterSet):
    """
    Фильтр для модели Student с расширенными возможностями.

    Поддерживает:
    - Фильтрация по курсу (множественный выбор)
    - Фильтрация по специальности (ID и название)
    - Фильтрация по навыкам (ID и название)
    - Фильтрация по городам (множественный выбор)
    - Фильтрация по возрасту (больше/меньше 18 лет)
    - Фильтрация по наличию опыта работы
    - Фильтрация по наличию портфолио
    - Полнотекстовый поиск
    """

    # Фильтр по курсу (множественный выбор)
    course = django_filters.MultipleChoiceFilter(
        choices=[(str(i), f'{i} курс') for i in range(1, 5)],
        field_name='course',
        lookup_expr='in',
        label='Курс'
    )

    # Фильтр по специальности по ID (множественный выбор)
    specialty = django_filters.ModelMultipleChoiceFilter(
        queryset=Specialty.objects.all(),
        field_name='specialty',
        to_field_name='id',
        label='Специальность (ID)'
    )

    # Фильтр по специальности по имени (множественный выбор)
    specialty_name = django_filters.MultipleChoiceFilter(
        choices=[],  # Заполняется динамически
        field_name='specialty__name',
        lookup_expr='in',
        label='Специальность (название)'
    )

    # Фильтр по навыкам по ID (множественный выбор)
    skills = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        field_name='skills',
        conjoined=False,  # OR логика: студент имеет хотя бы один из навыков
        label='Навыки (ID)'
    )

    # Фильтр по навыкам по имени (множественный выбор)
    skills_name = django_filters.MultipleChoiceFilter(
        choices=[],  # Заполняется динамически
        field_name='skills__name',
        lookup_expr='in',
        label='Навыки (название)'
    )

    # Фильтр по городу (множественный выбор)
    city = django_filters.MultipleChoiceFilter(
        choices=[],  # Заполняется динамически
        field_name='city',
        lookup_expr='in',
        label='Город'
    )

    # Фильтр по возрасту (больше 18 лет)
    over_18 = django_filters.BooleanFilter(
        method='filter_over_18',
        label='Старше 18 лет'
    )

    # Универсальный поиск
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

    # Фильтр по наличию заполненного профиля
    has_complete_profile = django_filters.BooleanFilter(
        method='filter_complete_profile',
        label='Заполненный профиль'
    )

    class Meta:
        model = Student
        fields = {
            'is_active': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически заполняем выбор городов
        self._update_city_choices()

        # Динамически заполняем выбор специальностей
        self._update_specialty_choices()

        # Динамически заполняем выбор навыков
        self._update_skills_choices()

    def _update_city_choices(self):
        """Динамически обновляет список городов."""
        cities = (
            Student.objects
            .exclude(city__isnull=True)
            .exclude(city='')
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )
        city_choices = [(city, city) for city in cities]
        self.filters['city'].extra['choices'] = city_choices

    def _update_specialty_choices(self):
        """Динамически обновляет список специальностей."""
        specialties = Specialty.objects.all().values_list('name', 'name').order_by('name')
        self.filters['specialty_name'].extra['choices'] = list(specialties)

    def _update_skills_choices(self):
        """Динамически обновляет список навыков."""
        skills = Skill.objects.all().values_list('name', 'name').order_by('name')
        # Можно добавить фильтрацию навыков по специальности
        specialty_ids = self.data.getlist('specialty') if self.data else []
        if specialty_ids:
            skills = (
                Skill.objects
                .filter(
                    Q(specialties__id__in=specialty_ids) |
                    Q(students__specialty__id__in=specialty_ids)
                )
                .distinct()
                .values_list('name', 'name')
                .order_by('name')
            )
        self.filters['skills_name'].extra['choices'] = list(skills)

    def filter_search(self, queryset, name, value):
        """
        Универсальный поиск по нескольким полям.

        Поиск осуществляется по:
        - Имени студента
        - Биографии
        - Городу
        - Названию навыков
        - Названию специальности
        """
        if not value:
            return queryset

        search_query = Q(full_name__icontains=value)
        search_query |= Q(bio__icontains=value)
        search_query |= Q(city__icontains=value)
        search_query |= Q(skills__name__icontains=value)
        search_query |= Q(specialty__name__icontains=value)

        return queryset.filter(search_query).distinct()

    def filter_has_experience(self, queryset, name, value):
        """
        Фильтрация по наличию опыта работы.

        Использует Exists для оптимизации запроса.
        """
        if value is True:
            from .models import WorkExperience
            has_work = Exists(
                WorkExperience.objects.filter(student=OuterRef('pk'))
            )
            return queryset.filter(has_work)
        elif value is False:
            from .models import WorkExperience
            has_work = Exists(
                WorkExperience.objects.filter(student=OuterRef('pk'))
            )
            return queryset.exclude(has_work)
        return queryset

    def filter_has_portfolio(self, queryset, name, value):
        """
        Фильтрация по наличию портфолио.

        Использует Exists для оптимизации запроса.
        """
        if value is True:
            from .models import Portfolio
            has_portfolio = Exists(
                Portfolio.objects.filter(student=OuterRef('pk'))
            )
            return queryset.filter(has_portfolio)
        elif value is False:
            from .models import Portfolio
            has_portfolio = Exists(
                Portfolio.objects.filter(student=OuterRef('pk'))
            )
            return queryset.exclude(has_portfolio)
        return queryset

    def filter_over_18(self, queryset, name, value):
        """
        Фильтрация по возрасту (больше или меньше 18 лет).

        Корректно учитывает високосные года и дату рождения.
        """
        if value is None:
            return queryset

        today = date.today()
        # Вычисляем дату 18 лет назад
        try:
            eighteen_years_ago = today.replace(year=today.year - 18)
        except ValueError:
            # Обработка 29 февраля в високосный год
            eighteen_years_ago = today.replace(year=today.year - 18, day=28)

        if value is True:
            # Старше 18 лет
            return queryset.filter(
                birth_date__lte=eighteen_years_ago
            ).exclude(birth_date__isnull=True)
        else:
            # Младше 18 лет
            return queryset.filter(
                birth_date__gt=eighteen_years_ago
            )

    def filter_complete_profile(self, queryset, name, value):
        """
        Фильтрация по заполненности профиля.

        Полный профиль включает:
        - Заполненную биографию
        - Хотя бы один навык
        - Специальность
        - Фото
        """
        if value is True:
            return (
                queryset
                .exclude(bio='')
                .exclude(specialty__isnull=True)
                .exclude(avatar='')
                .filter(skills__isnull=False)
                .distinct()
            )
        elif value is False:
            # Неполный профиль
            incomplete = Q(bio='') | Q(specialty__isnull=True) | Q(avatar='')
            return queryset.filter(incomplete).distinct()
        return queryset


# Дополнительные фильтры для будущего расширения

class SkillFilter(django_filters.FilterSet):
    """Фильтр для навыков."""

    category = django_filters.ModelChoiceFilter(
        queryset=lambda request: SkillCategory.objects.all(),
        field_name='category',
        label='Категория'
    )

    search = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск'
    )

    class Meta:
        from .models import Skill
        model = Skill
        fields = ['category']


class SpecialtyFilter(django_filters.FilterSet):
    """Фильтр для специальностей."""

    search = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск'
    )

    has_students = django_filters.BooleanFilter(
        method='filter_has_students',
        label='Есть студенты'
    )

    class Meta:
        model = Specialty
        fields = []

    def filter_has_students(self, queryset, name, value):
        """Фильтрация специальностей, у которых есть студенты."""
        if value is True:
            return queryset.filter(students__isnull=False).distinct()
        elif value is False:
            return queryset.filter(students__isnull=True)
        return queryset
