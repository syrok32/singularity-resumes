from django.db import models


class Skill(models.Model):
    name_skill = models.CharField(max_length=50, verbose_name='Skill name')

    def __str__(self):
        return self.name_skill


class Student(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=50, verbose_name='Имя')
    role = models.CharField(max_length=60, verbose_name='роль')
    photo_url = models.ImageField(upload_to='images/', verbose_name='фото', blank=True, null=True)
    skills = models.ManyToManyField(Skill, verbose_name='навыки')
    resume_url = models.URLField(verbose_name='резюме линк', blank=True, null=True)
    profile_url = models.URLField(verbose_name='профиль линк')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'студент'
        verbose_name_plural = 'Студенты'


class StudentProfiles(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ссылка на студента')

    description = models.TextField(verbose_name='Общее описание', blank=True)
    about = models.TextField(verbose_name='"Обо мне"', blank=True)
    resume_url = models.URLField(verbose_name='Ссылка на PDF', blank=True, null=True)
    skills = models.ManyToManyField(Skill, verbose_name='Технические навыки и стек', blank=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    telegram = models.CharField(max_length=100, verbose_name='Telegram', blank=True)
    phone = models.CharField(max_length=30, verbose_name='Телефон', blank=True)
    relocation_ready = models.BooleanField(verbose_name='Готов к переезду', default=False)
    relocation_city = models.CharField(max_length=100, blank=True, verbose_name='Город для переезда')

    experience = models.JSONField(verbose_name='Опыт работы', blank=True, default=list, null=True)
    education = models.JSONField(verbose_name='Образование', blank=True, default=list, null=True)
    projects = models.JSONField(verbose_name='Проекты', blank=True, default=list, null=True)
    socials = models.JSONField(verbose_name='Ссылки на соцсети и платформы', blank=True, default=dict, null=True)

    def __str__(self):
        return f"Профиль студента #{self.student.id}"

    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
        ordering = ['student__full_name']
