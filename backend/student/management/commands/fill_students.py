from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import SkillCategory, Skill, Specialty, Student, Education, WorkExperience, Portfolio
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Заполняет базу тестовыми студентами, навыками, образованием, опытом и портфолио"

    def handle(self, *args, **options):
        self.stdout.write("Начинаю создание тестовых данных студентов...")

        # Создаем категории навыков
        prog_cat, _ = SkillCategory.objects.get_or_create(name='Программирование')
        frontend_cat, _ = SkillCategory.objects.get_or_create(name='Фронтенд')
        backend_cat, _ = SkillCategory.objects.get_or_create(name='Бэкенд')
        db_cat, _ = SkillCategory.objects.get_or_create(name='Базы данных')
        mobile_cat, _ = SkillCategory.objects.get_or_create(name='Мобильная разработка')

        # Создаем навыки
        skills_data = [
            ('Python', prog_cat),
            ('JavaScript', prog_cat),
            ('Java', prog_cat),
            ('React', frontend_cat),
            ('Vue.js', frontend_cat),
            ('HTML', frontend_cat),
            ('CSS', frontend_cat),
            ('Django', backend_cat),
            ('Flask', backend_cat),
            ('Node.js', backend_cat),
            ('PostgreSQL', db_cat),
            ('MySQL', db_cat),
            ('React Native', mobile_cat),
            ('Flutter', mobile_cat),
        ]
        skills = {}
        for skill_name, category in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name, defaults={'category': category})
            skills[skill_name] = skill

        # Создаем специальности
        specialties_data = [
            'Веб-разработка',
            'Мобильная разработка',
            'Data Science',
            'Информационная безопасность',
            'Программная инженерия',
            'UI/UX Дизайн'
        ]
        specialties = {}
        for spec_name in specialties_data:
            specialty, created = Specialty.objects.get_or_create(name=spec_name)
            specialties[spec_name] = specialty

        # Данные студентов
        students_data = [
            {
                'email': 'ivan@example.com',
                'username': 'ivan_petrov',
                'full_name': 'Петров Иван Александрович',
                'course': '3',
                'bio': 'Студент 3 курса, увлекаюсь веб-разработкой и созданием полезных приложений.',
                'city': 'Москва',
                'phone_number': '89991234567',
                'birth_date': date(2001, 5, 15),
                'specialty': 'Веб-разработка',
                'skills': ['Python', 'Django', 'JavaScript', 'React'],
                'institution': 'МГУ им. М.В. Ломоносова',
                'position': 'Junior Python Developer',
                'company': 'Яндекс',
                'project_title': 'Todo приложение',
                'project_link': 'https://github.com/ivan/todo'
            },
            {
                'email': 'maria@example.com',
                'username': 'maria_sidorova',
                'full_name': 'Сидорова Мария Викторовна',
                'course': '4',
                'bio': 'Студентка 4 курса, специализируюсь на мобильной разработке.',
                'city': 'Санкт-Петербург',
                'phone_number': '89992345678',
                'birth_date': date(2000, 8, 22),
                'specialty': 'Мобильная разработка',
                'skills': ['React Native', 'JavaScript', 'Flutter'],
                'institution': 'СПбПУ',
                'position': 'Mobile Developer',
                'company': 'VK',
                'project_title': 'Мобильное приложение',
                'project_link': 'https://github.com/maria/mobile-app'
            },
            {
                'email': 'alex@example.com',
                'username': 'alex_kozlov',
                'full_name': 'Козлов Александр Дмитриевич',
                'course': '2',
                'bio': 'Студент 2 курса, изучаю Data Science и машинное обучение.',
                'city': 'Новосибирск',
                'phone_number': '89993456789',
                'birth_date': date(2002, 3, 10),
                'specialty': 'Data Science',
                'skills': ['Python', 'PostgreSQL'],
                'institution': 'НГУ',
                'position': 'Data Analyst',
                'company': 'Сбербанк',
                'project_title': 'Анализ данных',
                'project_link': 'https://github.com/alex/data-analysis'
            },
            {
                'email': 'elena@example.com',
                'username': 'elena_volkova',
                'full_name': 'Волкова Елена Сергеевна',
                'course': '3',
                'bio': 'Студентка 3 курса, специализируюсь на информационной безопасности.',
                'city': 'Екатеринбург',
                'phone_number': '89994567890',
                'birth_date': date(2001, 11, 5),
                'specialty': 'Информационная безопасность',
                'skills': ['Python', 'JavaScript'],
                'institution': 'УрФУ',
                'position': 'Security Analyst',
                'company': 'Kaspersky',
                'project_title': 'Система безопасности',
                'project_link': 'https://github.com/elena/security'
            },
            {
                'email': 'dmitry@example.com',
                'username': 'dmitry_novikov',
                'full_name': 'Новиков Дмитрий Андреевич',
                'course': '4',
                'bio': 'Студент 4 курса, fullstack разработчик.',
                'city': 'Казань',
                'phone_number': '89995678901',
                'birth_date': date(2000, 7, 18),
                'specialty': 'Программная инженерия',
                'skills': ['JavaScript', 'Node.js', 'React', 'Vue.js'],
                'institution': 'КФУ',
                'position': 'Fullstack Developer',
                'company': 'Тинькофф',
                'project_title': 'Веб-платформа',
                'project_link': 'https://github.com/dmitry/platform'
            },
            {
                'email': 'anna@example.com',
                'username': 'anna_petrova',
                'full_name': 'Петрова Анна Михайловна',
                'course': '2',
                'bio': 'Студентка 2 курса, изучаю UI/UX дизайн и фронтенд разработку.',
                'city': 'Ростов-на-Дону',
                'phone_number': '89996789012',
                'birth_date': date(2002, 12, 3),
                'specialty': 'UI/UX Дизайн',
                'skills': ['HTML', 'CSS', 'JavaScript', 'React'],
                'institution': 'ЮФУ',
                'position': 'UI/UX Designer',
                'company': 'Ozon',
                'project_title': 'Дизайн-система',
                'project_link': 'https://github.com/anna/design-system'
            },
        ]

        for data in students_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={'username': data['username']}
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Создан пользователь: {user.email}')

            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': data['full_name'],
                    'course': data['course'],
                    'bio': data['bio'],
                    'city': data['city'],
                    'phone_number': data['phone_number'],
                    'birth_date': data['birth_date'],
                    'specialty': specialties[data['specialty']],
                    'hh_link': f'https://hh.ru/resume/{random.randint(100000, 999999)}'
                }
            )
            if created:
                for skill_name in data['skills']:
                    skill = skills.get(skill_name)
                    if skill:
                        student.skills.add(skill)
                self.stdout.write(f'Создан студент: {student.full_name}')

                Education.objects.create(
                    student=student,
                    institution=data['institution'],
                    specialty=student.specialty,
                    start_year=2020,
                    end_year=2024,
                    additional_info='Факультет информационных технологий'
                )

                WorkExperience.objects.create(
                    student=student,
                    position=data['position'],
                    company=data['company'],
                    start_date=date(2023, 1, 15),
                    end_date=date(2023, 12, 31),
                    description='Разработка и поддержка проектов, участие в команде разработки.'
                )

                Portfolio.objects.create(
                    student=student,
                    title=data['project_title'],
                    link=data['project_link'],
                    description=f'Проект по специальности {student.specialty.name}'
                )

        self.stdout.write(self.style.SUCCESS('Все тестовые студенты успешно созданы!'))
