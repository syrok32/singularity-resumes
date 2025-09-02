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
