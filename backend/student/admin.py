"""
Административная панель Django для приложения student.
Оптимизирована для удобства управления и производительности.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Student, InternshipApplication, SkillCategory, Skill,
    Specialty, Education, WorkExperience, Portfolio, Employer
)


# Inline классы для вложенного редактирования

class EducationInline(admin.TabularInline):
    """Inline для образования студента."""
    model = Education
    extra = 1
    fields = ('institution', 'specialty', 'start_year', 'end_year', 'additional_info')
    autocomplete_fields = ['specialty']


class WorkExperienceInline(admin.TabularInline):
    """Inline для опыта работы студента."""
    model = WorkExperience
    extra = 1
    fields = ('position', 'company', 'start_date', 'end_date', 'description')


class PortfolioInline(admin.TabularInline):
    """Inline для портфолио студента."""
    model = Portfolio
    extra = 1
    fields = ('title', 'link', 'description')


# Основные ModelAdmin классы

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Админка для категорий навыков."""

    list_display = ('id', 'name', 'skills_count')
    search_fields = ('name',)
    ordering = ('name',)

    def skills_count(self, obj):
        """Отображает количество навыков в категории."""
        return obj.skills.count()

    skills_count.short_description = 'Количество навыков'

    def get_queryset(self, request):
        """Оптимизация: предзагрузка количества навыков."""
        qs = super().get_queryset(request)
        return qs.annotate(skills_count_annotated=Count('skills'))


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Админка для навыков."""

    list_display = ('id', 'name', 'category', 'student_count')
    list_filter = ('category',)
    search_fields = ('name',)
    autocomplete_fields = ['category']
    ordering = ('name',)

    def student_count(self, obj):
        """Отображает количество студентов с этим навыком."""
        count = obj.students.filter(is_active=True).count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'gray',
            count
        )

    student_count.short_description = 'Активных студентов'

    def get_queryset(self, request):
        """Оптимизация: предзагрузка категории."""
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Админка для специальностей."""

    list_display = ('id', 'name', 'student_count', 'skills_count')
    search_fields = ('name',)
    filter_horizontal = ('skills',)
    ordering = ('name',)

    def student_count(self, obj):
        """Отображает количество студентов."""
        count = obj.students.filter(is_active=True).count()
        url = reverse('admin:student_student_changelist') + f'?specialty__id__exact={obj.id}'
        return format_html('<a href="{}">{} студентов</a>', url, count)

    student_count.short_description = 'Студентов'

    def skills_count(self, obj):
        """Отображает количество навыков."""
        return obj.skills.count()

    skills_count.short_description = 'Навыков'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Админка для студентов."""

    list_display = (
        'id', 'avatar_preview', 'full_name', 'user_email',
        'course', 'specialty', 'city', 'skills_count',
        'is_active_colored', 'created_at'
    )
    list_filter = (
        'is_active', 'course', 'specialty', 'city',
        'created_at', 'updated_at'
    )
    search_fields = (
        'full_name', 'user__email', 'city', 'bio',
        'skills__name', 'specialty__name'
    )
    readonly_fields = (
        'avatar_preview_large', 'age', 'created_at',
        'updated_at', 'has_experience', 'has_portfolio'
    )
    autocomplete_fields = ['user', 'specialty']
    filter_horizontal = ('skills',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'user', 'avatar', 'avatar_preview_large', 'is_active')
        }),
        ('Личные данные', {
            'fields': ('birth_date', 'age', 'phone_number', 'city')
        }),
        ('Учебная информация', {
            'fields': ('course', 'specialty', 'skills')
        }),
        ('Профессиональная информация', {
            'fields': ('bio', 'hh_link', 'has_experience', 'has_portfolio')
        }),
        ('Telegram', {
            'fields': ('telegram_user_id', 'telegram_chat_id'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [EducationInline, WorkExperienceInline, PortfolioInline]

    actions = ['activate_students', 'deactivate_students']

    def avatar_preview(self, obj):
        """Миниатюра аватара в списке."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return '—'

    avatar_preview.short_description = 'Фото'

    def avatar_preview_large(self, obj):
        """Превью аватара в форме редактирования."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.avatar.url
            )
        return 'Аватар не загружен'

    avatar_preview_large.short_description = 'Превью аватара'

    def user_email(self, obj):
        """Отображает email пользователя."""
        return obj.user.email

    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def skills_count(self, obj):
        """Количество навыков студента."""
        count = obj.skills.count()
        return format_html('<b>{}</b>', count)

    skills_count.short_description = 'Навыки'

    def is_active_colored(self, obj):
        """Цветной индикатор активности."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Активен</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Неактивен</span>'
        )

    is_active_colored.short_description = 'Статус'
    is_active_colored.admin_order_field = 'is_active'

    def activate_students(self, request, queryset):
        """Массовая активация студентов."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано студентов: {updated}')

    activate_students.short_description = 'Активировать выбранных студентов'

    def deactivate_students(self, request, queryset):
        """Массовая деактивация студентов."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано студентов: {updated}')

    deactivate_students.short_description = 'Деактивировать выбранных студентов'

    def get_queryset(self, request):
        """Оптимизация запросов."""
        qs = super().get_queryset(request)
        return qs.select_related('specialty', 'user').prefetch_related('skills')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Админка для образования."""

    list_display = ('id', 'student_link', 'institution', 'specialty', 'period')
    list_filter = ('specialty', 'start_year', 'end_year')
    search_fields = ('student__full_name', 'institution', 'specialty__name')
    autocomplete_fields = ['student', 'specialty']

    def student_link(self, obj):
        """Ссылка на студента."""
        url = reverse('admin:student_student_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.full_name)

    student_link.short_description = 'Студент'

    def period(self, obj):
        """Период обучения."""
        end = obj.end_year or 'н.в.'
        return f'{obj.start_year}–{end}'

    period.short_description = 'Период'

    def get_queryset(self, request):
        """Оптимизация запросов."""
        qs = super().get_queryset(request)
        return qs.select_related('student', 'specialty')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    """Админка для опыта работы."""

    list_display = ('id', 'student_link', 'position', 'company', 'period', 'is_current')
    list_filter = ('start_date', 'end_date')
    search_fields = ('student__full_name', 'position', 'company')
    autocomplete_fields = ['student']
    date_hierarchy = 'start_date'

    def student_link(self, obj):
        """Ссылка на студента."""
        url = reverse('admin:student_student_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.full_name)

    student_link.short_description = 'Студент'

    def period(self, obj):
        """Период работы."""
        end = obj.end_date.strftime('%m.%Y') if obj.end_date else 'н.в.'
        return f'{obj.start_date.strftime("%m.%Y")} – {end}'

    period.short_description = 'Период'

    def is_current(self, obj):
        """Текущая работа."""
        if obj.end_date is None:
            return format_html('<span style="color: green;">✓ Текущая</span>')
        return '—'

    is_current.short_description = 'Статус'

    def get_queryset(self, request):
        """Оптимизация запросов."""
        qs = super().get_queryset(request)
        return qs.select_related('student')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Админка для портфолио."""

    list_display = ('id', 'student_link', 'title', 'link_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__full_name', 'title', 'description')
    autocomplete_fields = ['student']
    date_hierarchy = 'created_at'

    def student_link(self, obj):
        """Ссылка на студента."""
        url = reverse('admin:student_student_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.full_name)

    student_link.short_description = 'Студент'

    def link_preview(self, obj):
        """Превью ссылки."""
        if obj.link:
            return format_html('<a href="{}" target="_blank">🔗 Открыть</a>', obj.link)
        return '—'

    link_preview.short_description = 'Ссылка'

    def get_queryset(self, request):
        """Оптимизация запросов."""
        qs = super().get_queryset(request)
        return qs.select_related('student')


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    """Админка для работодателей."""

    list_display = ('id', 'name', 'email', 'telegram_id', 'applications_count', 'created_at')
    search_fields = ('name', 'email', 'telegram_id')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def applications_count(self, obj):
        """Количество заявок."""
        count = obj.applications.count()
        if count > 0:
            url = reverse('admin:student_internshipapplication_changelist') + f'?employer__id__exact={obj.id}'
            return format_html('<a href="{}">{} заявок</a>', url, count)
        return '0'

    applications_count.short_description = 'Заявок'


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    """Админка для заявок на стажировку."""

    list_display = (
        'id', 'student_link', 'employer_link', 'status_colored',
        'sla_deadline', 'reminder_sent', 'created_at'
    )
    list_filter = ('status', 'reminder_sent', 'employer_registered', 'created_at')
    search_fields = ('student__full_name', 'employer__name', 'message')
    readonly_fields = (
        'tracking_token', 'created_at', 'updated_at',
        'employer_registration_datetime'
    )
    autocomplete_fields = ['student', 'employer']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('student', 'employer', 'message', 'status')
        }),
        ('Ответы', {
            'fields': ('student_response', 'moderator_response')
        }),
        ('Telegram', {
            'fields': (
                'telegram_user_id', 'employer_telegram_user_id',
                'chat_id', 'chat_created'
            ),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': (
                'company_name', 'employer_email', 'employer_registered',
                'employer_registration_datetime'
            ),
            'classes': ('collapse',)
        }),
        ('SLA и отслеживание', {
            'fields': ('sla_deadline', 'reminder_sent', 'tracking_token')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_accepted', 'mark_as_rejected']

    def student_link(self, obj):
        """Ссылка на студента."""
        url = reverse('admin:student_student_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.full_name)

    student_link.short_description = 'Студент'

    def employer_link(self, obj):
        """Ссылка на работодателя."""
        url = reverse('admin:student_employer_change', args=[obj.employer.id])
        return format_html('<a href="{}">{}</a>', url, obj.employer.name)

    employer_link.short_description = 'Работодатель'

    def status_colored(self, obj):
        """Цветной индикатор статуса."""
        colors = {
            'pending': 'orange',
            'accepted': 'green',
            'rejected': 'red',
            'completed': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_colored.short_description = 'Статус'
    status_colored.admin_order_field = 'status'

    def mark_as_accepted(self, request, queryset):
        """Массовое принятие заявок."""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'Принято заявок: {updated}')

    mark_as_accepted.short_description = 'Пометить как принятые'

    def mark_as_rejected(self, request, queryset):
        """Массовое отклонение заявок."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Отклонено заявок: {updated}')

    mark_as_rejected.short_description = 'Пометить как отклонённые'

    def get_queryset(self, request):
        """Оптимизация запросов."""
        qs = super().get_queryset(request)
        return qs.select_related('student', 'employer')


# Кастомизация заголовков админки
admin.site.site_header = 'Singularity Resume - Админ-панель'
admin.site.site_title = 'Singularity Resume'
admin.site.index_title = 'Управление платформой'
