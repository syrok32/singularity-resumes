from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Категория навыков', db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория навыка'
        verbose_name_plural = 'Категории навыков'


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Навык', db_index=True)
    category = models.ForeignKey('SkillCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'





class Specialty(models.Model):

    name = models.CharField(max_length=100, verbose_name='Специальность')
    skills = models.ManyToManyField('Skill', blank=True, related_name='specialties', verbose_name='Навыки специальности')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'



class Education(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='educations', verbose_name='Студент')
    institution = models.CharField(max_length=255, verbose_name='Учебное заведение')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    start_year = models.PositiveIntegerField(verbose_name='Год начала')
    end_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Год окончания')
    additional_info = models.TextField(blank=True, verbose_name='Дополнительная информация')

    def __str__(self):
        return f"{self.institution} ({self.start_year}-{self.end_year or 'н.в.'})"

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образования'


class WorkExperience(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='work_experiences', verbose_name='Студент')
    position = models.CharField(max_length=255, verbose_name='Должность')
    company = models.CharField(max_length=255, verbose_name='Компания')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return f"{self.position} at {self.company}"

    class Meta:
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'


class Portfolio(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='portfolios', verbose_name='Студент')
    title = models.CharField(max_length=255, verbose_name='Название')
    link = models.URLField(blank=True, verbose_name='Ссылка')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Портфолио'
        verbose_name_plural = 'Портфолио'


class Student(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО", blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    avatar = models.ImageField(upload_to="images/students/", blank=True, null=True, verbose_name='Аватар')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    course = models.CharField(
        max_length=50,
        choices=[(str(i), str(i)) for i in range(1, 5)],
        verbose_name="Курс"
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    hh_link = models.URLField(blank=True, verbose_name='Ссылка на HH')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    skills = models.ManyToManyField(Skill, blank=True, verbose_name='Навыки')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Специальность')

    # Telegram related fields (optional denormalization for easy joins)
    telegram_user_id = models.BigIntegerField(null=True, blank=True, db_index=True, verbose_name='TG user id')
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, verbose_name='TG chat id')

    def __str__(self):

        return self.full_name or str(self.user)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['course']),
        ]

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None


class InternshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='applications', verbose_name='Студент')
    employer_name = models.CharField(max_length=255, verbose_name='Работодатель')
    message = models.TextField(verbose_name='Сообщение')
    # контакт email
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    student_response = models.CharField(max_length=20, choices=[('accepted','Принято'),('rejected','Отклонено'),('pending','Ожидает')], default='pending', verbose_name='Ответ студента')
    moderator_response = models.CharField(max_length=20, choices=[('accepted','Принято'),('rejected','Отклонено'),('pending','Ожидает')], default='pending', verbose_name='Ответ куратора')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def recompute_status(self):
        if self.student_response == 'accepted' and self.moderator_response == 'accepted':
            self.status = 'accepted'
        elif self.student_response == 'rejected' or self.moderator_response == 'rejected':
            self.status = 'rejected'
        else:
            self.status = 'pending'

    def save(self, *args, **kwargs):
        self.recompute_status()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заявка на стажировку'
        verbose_name_plural = 'Заявки на стажировку'
