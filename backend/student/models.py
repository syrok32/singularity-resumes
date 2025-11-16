"""
Модели для приложения student.
Оптимизированы для производительности и расширяемости.
"""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
import secrets


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с временными метками.
    Используется для всех моделей, требующих отслеживания времени создания и обновления.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        abstract = True

class StudentManager(models.Manager):
    def get_queryset(self):
        return StudentQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_full_profile(self):
        return self.get_queryset().with_full_profile()

    def with_card_data(self):
        return self.get_queryset().with_card_data()
class StudentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_full_profile(self):
        return (
            self.select_related('specialty', 'user')
                .prefetch_related(
                    'skills__category',
                    'educations__specialty',
                    'work_experiences',
                    'portfolios'
                )
        )

    def with_card_data(self):
        return (
            self.select_related('specialty', 'user')
                .prefetch_related('skills')
                .only(
                    'id', 'full_name', 'avatar', 'course', 'bio',
                    'specialty__name', 'user__email'
                )
        )
class SkillCategoryManager(models.Manager):
    """Менеджер для оптимизированных запросов категорий навыков."""

    def with_skills_count(self):
        """Возвращает категории с количеством навыков."""
        return self.annotate(skills_count=models.Count('skill'))


class SkillCategory(models.Model):
    """Категория навыков (например: Backend, Frontend, DevOps)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Категория навыков'),
        db_index=True
    )

    objects = SkillCategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Категория навыка')
        verbose_name_plural = _('Категории навыков')
        ordering = ['name']


class SkillManager(models.Manager):
    """Менеджер для оптимизированных запросов навыков."""

    def with_category(self):
        """Оптимизация запросов с предзагрузкой категории."""
        return self.select_related('category')

    def popular(self, limit=10):
        """Возвращает самые популярные навыки по количеству студентов."""
        return (self.with_category()
                .annotate(student_count=models.Count('student', filter=models.Q(student__is_active=True)))
                .filter(student_count__gt=0)
                .order_by('-student_count')[:limit])


class Skill(models.Model):
    """Навык студента."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Навык'),
        db_index=True
    )
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Категория'),
        related_name='skills'
    )

    objects = SkillManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Навык')
        verbose_name_plural = _('Навыки')
        ordering = ['name']


class SpecialtyManager(models.Manager):
    """Менеджер для оптимизированных запросов специальностей."""

    def with_skills(self):
        """Предзагрузка навыков для специальности."""
        return self.prefetch_related('skills')

    def with_student_count(self):
        """Возвращает специальности с количеством активных студентов."""
        return self.annotate(
            student_count=models.Count('student', filter=models.Q(student__is_active=True))
        )


class Specialty(models.Model):
    """Специальность/профессия студента."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Специальность'),
        db_index=True
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='specialties',
        verbose_name=_('Навыки специальности')
    )

    objects = SpecialtyManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Специальность')
        verbose_name_plural = _('Специальности')
        ordering = ['name']



class Student(TimeStampedModel):
    """Профиль студента."""

    # Основная информация
    full_name = models.CharField(
        max_length=200,
        verbose_name=_("ФИО"),
        db_index=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='student_profile'
    )
    avatar = models.ImageField(
        upload_to="images/students/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    # Контактная информация
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата рождения')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Номер телефона")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Город'),
        db_index=True
    )

    # Учебная информация
    course = models.CharField(
        max_length=1,
        choices=[(str(i), f'{i} курс') for i in range(1, 5)],
        verbose_name=_("Курс"),
        db_index=True
    )

    # Профессиональная информация
    bio = models.TextField(
        blank=True,
        verbose_name=_('Биография'),
        help_text=_('Краткое описание студента')
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Специальность'),
        related_name='students'
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        verbose_name=_('Навыки'),
        related_name='students'
    )
    hh_link = models.URLField(
        blank=True,
        verbose_name=_('Ссылка на HeadHunter')
    )

    # Статус и активность
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен'),
        db_index=True,
        help_text=_('Показывать профиль на сайте')
    )

    # Telegram интеграция
    telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        unique=True,
        verbose_name=_('Telegram User ID')
    )
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Telegram Chat ID')
    )

    objects = StudentManager()

    def __str__(self):
        return self.full_name or self.user.email

    @property
    def age(self):
        """Вычисляет возраст студента."""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def avatar_url(self):
        """Возвращает URL аватара или None."""
        return self.avatar.url if self.avatar else None

    @property
    def has_experience(self):
        """Проверяет наличие опыта работы."""
        return self.work_experiences.exists()

    @property
    def has_portfolio(self):
        """Проверяет наличие портфолио."""
        return self.portfolios.exists()

    class Meta:
        verbose_name = _('Студент')
        verbose_name_plural = _('Студенты')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'course']),
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['specialty', 'is_active']),
        ]


class Education(TimeStampedModel):
    """Образование студента."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='educations',
        verbose_name=_('Студент')
    )
    institution = models.CharField(
        max_length=255,
        verbose_name=_('Учебное заведение')
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Специальность')
    )
    start_year = models.PositiveIntegerField(
        verbose_name=_('Год начала'),
        validators=[MinValueValidator(1950), MaxValueValidator(2100)]
    )
    end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Год окончания'),
        validators=[MinValueValidator(1950), MaxValueValidator(2100)]
    )
    additional_info = models.TextField(
        blank=True,
        verbose_name=_('Дополнительная информация')
    )

    def __str__(self):
        end = self.end_year or 'н.в.'
        return f"{self.institution} ({self.start_year}-{end})"

    class Meta:
        verbose_name = _('Образование')
        verbose_name_plural = _('Образование')
        ordering = ['-start_year']


class WorkExperience(TimeStampedModel):
    """Опыт работы студента."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='work_experiences',
        verbose_name=_('Студент')
    )
    position = models.CharField(
        max_length=255,
        verbose_name=_('Должность')
    )
    company = models.CharField(
        max_length=255,
        verbose_name=_('Компания')
    )
    start_date = models.DateField(
        verbose_name=_('Дата начала')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата окончания')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )

    def __str__(self):
        return f"{self.position} в {self.company}"

    class Meta:
        verbose_name = _('Опыт работы')
        verbose_name_plural = _('Опыт работы')
        ordering = ['-start_date']


class Portfolio(TimeStampedModel):
    """Портфолио/проект студента."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='portfolios',
        verbose_name=_('Студент')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название проекта')
    )
    link = models.URLField(
        blank=True,
        verbose_name=_('Ссылка на проект')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание проекта')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Портфолио')
        verbose_name_plural = _('Портфолио')
        ordering = ['-created_at']


class Employer(TimeStampedModel):
    """Работодатель."""

    name = models.CharField(
        max_length=255,
        verbose_name=_('Название компании')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    telegram_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Telegram ID')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Работодатель")
        verbose_name_plural = _("Работодатели")


class InternshipApplicationManager(models.Manager):
    """Менеджер для заявок на стажировку."""

    def pending(self):
        """Возвращает ожидающие заявки."""
        return self.filter(status='pending')

    def with_relations(self):
        """Оптимизация запросов с предзагрузкой связей."""
        return self.select_related('student', 'employer')


class InternshipApplication(TimeStampedModel):
    """Заявка на стажировку от работодателя к студенту."""

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Студент')
    )
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Работодатель')
    )
    message = models.TextField(
        verbose_name=_('Сообщение')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус'),
        db_index=True
    )

    # Telegram интеграция
    telegram_user_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Telegram ID отправителя')
    )
    employer_telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Telegram ID работодателя')
    )
    chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID чата')
    )
    chat_created = models.BooleanField(
        default=False,
        verbose_name=_('Чат создан')
    )

    # Дополнительная информация
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Название компании')
    )
    employer_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email работодателя')
    )
    employer_registered = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Работодатель зарегистрирован')
    )
    employer_registration_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата регистрации работодателя')
    )

    # Ответы и отслеживание
    student_response = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Ответ студента')
    )
    moderator_response = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Ответ модератора')
    )
    tracking_token = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Токен отслеживания')
    )

    # SLA и напоминания
    sla_deadline = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_('Крайний срок SLA')
    )
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name=_('Напоминание отправлено')
    )

    objects = InternshipApplicationManager()

    def __str__(self):
        return f"Заявка #{self.id} от {self.employer} для {self.student}"

    def save(self, *args, **kwargs):
        """Автоматическая генерация tracking_token при создании."""
        if not self.tracking_token:
            self.tracking_token = self.generate_tracking_token()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_tracking_token():
        """Генерирует безопасный токен для deep-link."""
        return secrets.token_urlsafe(16)

    def is_employer_registered(self):
        """Проверяет, зарегистрирован ли работодатель в боте."""
        return self.employer_registered and self.employer_telegram_user_id

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Заявка на стажировку")
        verbose_name_plural = _("Заявки на стажировку")
        indexes = [
            models.Index(fields=['status', 'sla_deadline']),
            models.Index(fields=['employer_registered', 'created_at']),
            models.Index(fields=['student', 'status']),
        ]
