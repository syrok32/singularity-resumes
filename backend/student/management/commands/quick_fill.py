from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import SkillCategory, Skill, Specialty, Student, Education, WorkExperience, Portfolio
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Quick fill database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создаем категории навыков
        prog_cat, _ = SkillCategory.objects.get_or_create(name='Программирование')
        frontend_cat, _ = SkillCategory.objects.get_or_create(name='Фронтенд')
        backend_cat, _ = SkillCategory.objects.get_or_create(name='Бэкенд')
        
        # Создаем навыки
        python_skill, _ = Skill.objects.get_or_create(name='Python', defaults={'category': prog_cat})
        js_skill, _ = Skill.objects.get_or_create(name='JavaScript', defaults={'category': prog_cat})
        react_skill, _ = Skill.objects.get_or_create(name='React', defaults={'category': frontend_cat})
        django_skill, _ = Skill.objects.get_or_create(name='Django', defaults={'category': backend_cat})
        
        # Создаем специальности
        web_spec, _ = Specialty.objects.get_or_create(name='Веб-разработка')
        
        # Создаем пользователя
        user, created = User.objects.get_or_create(
            email='ivan@example.com',
            defaults={'username': 'ivan_petrov'}
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Создан пользователь: {user.email}')
        
        # Создаем студента
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'Петров Иван',
                'course': '3',
                'bio': 'Студент 3 курса',
                'city': 'Москва',
                'phone_number': '89991234567',  # Короткий номер
                'birth_date': date(2001, 5, 15),
                'specialty': web_spec,
                'hh_link': 'https://hh.ru/resume/123456'
            }
        )
        
        if created:
            # Добавляем навыки
            student.skills.add(python_skill, js_skill, react_skill, django_skill)
            
            self.stdout.write(f'Создан студент: {student.full_name}')
            
            # Создаем образование
            Education.objects.create(
                student=student,
                institution='МГУ',
                specialty=web_spec,
                start_year=2020,
                end_year=2024,
                additional_info='ВМК'
            )
            
            # Создаем опыт работы
            WorkExperience.objects.create(
                student=student,
                position='Junior Developer',
                company='Яндекс',
                start_date=date(2023, 1, 15),
                end_date=date(2023, 12, 31),
                description='Разработка веб-приложений'
            )
            
            # Создаем портфолио
            Portfolio.objects.create(
                student=student,
                title='Todo App',
                link='https://github.com/ivan/todo',
                description='Приложение для задач'
            )
        
        self.stdout.write(self.style.SUCCESS('Данные созданы!'))