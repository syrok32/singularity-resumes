from django.db import models


class Skill(models.Model):
    name_skill = models.CharField(max_length=50, verbose_name='Skill name')

    def __str__(self):
        return self.name_skill

    class Meta:
        verbose_name = 'скилл'
        verbose_name_plural = 'скиллы'


class Student(models.Model):
    full_name = models.CharField(max_length=50, verbose_name='Имя')
    role = models.CharField(max_length=60, verbose_name='роль')
    top_skills = models.ManyToManyField(Skill, verbose_name='навыки')
    short_description = models.TextField(verbose_name='', blank=True)
    photo_url = models.ImageField(upload_to='images/students/', verbose_name='фото', blank=True,
                                  null=True)
    profile_url = models.URLField(verbose_name='профиль линк')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'студент'
        verbose_name_plural = 'Студенты'


class StudentDetail(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='Ссылка на студента')
    skills = models.ManyToManyField(
        Skill, verbose_name='Технические навыки и стек', blank=True)
    description = models.TextField(verbose_name='Общее описание', blank=True)

    # about = models.TextField(verbose_name='"Обо мне"', blank=True)
    # resume_url = models.URLField(verbose_name='Ссылка на PDF', blank=True, null=True)
    # email = models.EmailField(verbose_name='Email', blank=True, null=True)
    # telegram = models.CharField(max_length=100, verbose_name='Telegram', blank=True)
    # phone = models.CharField(max_length=30, verbose_name='Телефон', blank=True)
    # relocation_ready = models.BooleanField(verbose_name='Готов к переезду', default=False)
    # relocation_city = models.CharField(max_length=100, blank=True, verbose_name='Город для переезда')

    def __str__(self):
        return f"Профиль студента #{self.student.id}"

    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
        ordering = ['student__full_name']
