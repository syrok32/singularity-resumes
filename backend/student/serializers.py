"""
Сериализаторы для приложения student.
Оптимизированы для производительности и удобства фронтенда.
"""

from rest_framework import serializers
from .models import (
    Skill, SkillCategory, Specialty, Education,
    WorkExperience, Portfolio, Student
)


class SkillCategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории навыков."""

    class Meta:
        model = SkillCategory
        fields = ['id', 'name']
        read_only_fields = ['id']


class SkillSerializer(serializers.ModelSerializer):
    """Сериализатор навыка с категорией."""

    category = SkillCategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'category_name']
        read_only_fields = ['id']


class SkillListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор навыка для списков."""

    class Meta:
        model = Skill
        fields = ['id', 'name']
        read_only_fields = ['id']


class SpecialtySerializer(serializers.ModelSerializer):
    """Сериализатор специальности."""

    class Meta:
        model = Specialty
        fields = ['id', 'name']
        read_only_fields = ['id']


class SpecialtyDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор специальности с навыками."""

    skills = SkillListSerializer(many=True, read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Specialty
        fields = ['id', 'name', 'skills', 'student_count']
        read_only_fields = ['id']


class EducationSerializer(serializers.ModelSerializer):
    """Сериализатор образования."""

    specialty = SpecialtySerializer(read_only=True)
    specialty_name = serializers.CharField(source='specialty.name', read_only=True, allow_null=True)
    period = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'specialty', 'specialty_name',
            'start_year', 'end_year', 'period', 'is_current',
            'additional_info'
        ]
        read_only_fields = ['id']

    def get_period(self, obj):
        """Возвращает период обучения в формате '2020-2024' или '2020-н.в.'"""
        end = obj.end_year or 'н.в.'
        return f"{obj.start_year}–{end}"

    def get_is_current(self, obj):
        """Определяет, является ли обучение текущим."""
        return obj.end_year is None


class WorkExperienceSerializer(serializers.ModelSerializer):
    """Сериализатор опыта работы."""

    period = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    duration_months = serializers.SerializerMethodField()

    class Meta:
        model = WorkExperience
        fields = [
            'id', 'position', 'company', 'start_date', 'end_date',
            'period', 'is_current', 'duration_months', 'description'
        ]
        read_only_fields = ['id']

    def get_period(self, obj):
        """Возвращает период работы."""
        from datetime import date
        start = obj.start_date.strftime('%m.%Y')
        end = obj.end_date.strftime('%m.%Y') if obj.end_date else 'н.в.'
        return f"{start} – {end}"

    def get_is_current(self, obj):
        """Определяет, является ли работа текущей."""
        return obj.end_date is None

    def get_duration_months(self, obj):
        """Вычисляет продолжительность работы в месяцах."""
        from datetime import date
        end = obj.end_date or date.today()
        start = obj.start_date
        months = (end.year - start.year) * 12 + (end.month - start.month)
        return max(months, 1)


class PortfolioSerializer(serializers.ModelSerializer):
    """Сериализатор портфолио/проекта."""

    has_link = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'link', 'has_link', 'description']
        read_only_fields = ['id']

    def get_has_link(self, obj):
        """Проверяет наличие ссылки."""
        return bool(obj.link)


class StudentCardSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для карточки студента в списке.
    Оптимизирован для минимального объема данных.
    """

    specialty = serializers.CharField(source='specialty.name', read_only=True, allow_null=True)
    skills = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'avatar_url', 'course',
            'specialty', 'skills', 'description', 'city', 'age'
        ]
        read_only_fields = ['id', 'avatar_url', 'age']

    def get_skills(self, obj):
        """
        Возвращает топ-5 навыков студента.
        Оптимизировано: использует prefetch_related из ViewSet.
        """
        # Если навыки уже prefetch-нуты, избегаем дополнительных запросов
        skills = list(obj.skills.all()[:5])
        return [skill.name for skill in skills]

    def get_description(self, obj):
        """Возвращает краткое описание (первые 100 символов био)."""
        if not obj.bio:
            return ""
        text = obj.bio.strip()
        if len(text) <= 100:
            return text
        return text[:100].rsplit(' ', 1) + '…'


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор профиля студента.
    Включает все связанные данные.
    """

    # Связанные поля
    specialty = SpecialtySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)

    # Дополнительные поля
    email = serializers.EmailField(source='user.email', read_only=True)
    age = serializers.IntegerField(read_only=True)

    # Метаинформация
    has_experience = serializers.BooleanField(read_only=True)
    has_portfolio = serializers.BooleanField(read_only=True)
    experience_count = serializers.SerializerMethodField()
    portfolio_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            # Основная информация
            'id', 'full_name', 'email', 'avatar_url',

            # Личная информация
            'birth_date', 'age', 'phone_number', 'city',

            # Учебная информация
            'course', 'specialty',

            # Профессиональная информация
            'bio', 'skills', 'hh_link',

            # Опыт и портфолио
            'educations', 'work_experiences', 'portfolios',

            # Метаинформация
            'has_experience', 'has_portfolio',
            'experience_count', 'portfolio_count',

            # Статус
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'avatar_url', 'age', 'has_experience',
            'has_portfolio', 'created_at', 'updated_at'
        ]

    def get_experience_count(self, obj):
        """Возвращает количество записей опыта работы."""
        # Используем prefetch_related из ViewSet
        return obj.work_experiences.count()

    def get_portfolio_count(self, obj):
        """Возвращает количество проектов в портфолио."""
        # Используем prefetch_related из ViewSet
        return obj.portfolios.count()


class StudentListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для топ-студентов на главной странице.
    Минимальный набор данных для карусели/слайдера.
    """

    specialty = serializers.CharField(source='specialty.name', read_only=True, allow_null=True)
    top_skills = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'avatar_url',
            'specialty', 'top_skills', 'course'
        ]
        read_only_fields = ['id', 'avatar_url']

    def get_top_skills(self, obj):
        """Возвращает топ-3 навыка для главной страницы."""
        skills = list(obj.skills.all()[:3])
        return [skill.name for skill in skills]


# Сериализаторы для статистики и фильтров

class FilterOptionsSerializer(serializers.Serializer):
    """Сериализатор опций для фильтров."""

    specialties = SpecialtySerializer(many=True)
    skills = SkillSerializer(many=True)
    courses = serializers.ListField(child=serializers.DictField())
    cities = serializers.ListField(child=serializers.CharField())
    skills_by_category = serializers.DictField()


class CourseStatsSerializer(serializers.Serializer):
    """Сериализатор статистики по курсам."""

    course = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class SpecialtyStatsSerializer(serializers.Serializer):
    """Сериализатор статистики по специальностям."""

    name = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class SkillStatsSerializer(serializers.Serializer):
    """Сериализатор статистики по навыкам."""

    name = serializers.CharField()
    count = serializers.IntegerField()
    category = serializers.CharField()


class CityStatsSerializer(serializers.Serializer):
    """Сериализатор статистики по городам."""

    name = serializers.CharField()
    count = serializers.IntegerField()


class StudentStatsSerializer(serializers.Serializer):
    """Общий сериализатор статистики студентов."""

    total_students = serializers.IntegerField()
    course_stats = CourseStatsSerializer(many=True)
    specialty_stats = SpecialtyStatsSerializer(many=True)
    top_skills = SkillStatsSerializer(many=True)
    city_stats = CityStatsSerializer(many=True)
