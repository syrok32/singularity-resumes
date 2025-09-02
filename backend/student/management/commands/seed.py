from django.core.management.base import BaseCommand
from student.models import Students, StudentProfile, Skill, StudentSkill, Education, Experience, Project, Language

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        # Очистка существующих данных
        Students.objects.all().delete()
        StudentProfile.objects.all().delete()
        Skill.objects.all().delete()
        StudentSkill.objects.all().delete()
        Education.objects.all().delete()
        Experience.objects.all().delete()
        Project.objects.all().delete()
        Language.objects.all().delete()

        # Создание навыков
        skills = [
            Skill(name_skill='Python', skill_type='hard'),
            Skill(name_skill='Java', skill_type='hard'),
            Skill(name_skill='Коммуникация', skill_type='soft'),
        ]
        Skill.objects.bulk_create(skills)

        # Создание языков
        languages = [
            Language(name='English', level='B2'),
            Language(name='Русский', level='C2'),
        ]
        Language.objects.bulk_create(languages)

        # Создание студента
        student = Students.objects.create(
            full_name='Роман Боронов',
            role='developer',
            custom_role='',
            short_description='Опытный разработчик с фокусом на Java.',
            course_rating=4
        )

        # Создание профиля
        profile = StudentProfile.objects.create(
            student=student,
            status_work='ищу работу',
            age=25,
            city='Москва',
            relocation_ready=True,
            about='Люблю программирование и участвую в хакатонах.'
        )

        # Добавление топ-скиллов
        student.top_skills.set([skills[0], skills[1]])  # Python, Java

        # Добавление навыков с уровнями
        student_skills = [
            StudentSkill(student=profile, skill=skills[0], proficiency=70),  # Python 70%
            StudentSkill(student=profile, skill=skills[1], proficiency=50),  # Java 50%
            StudentSkill(student=profile, skill=skills[2], proficiency=80),  # Коммуникация 80%
        ]
        StudentSkill.objects.bulk_create(student_skills)

        # Добавление языков
        profile.languages.set(languages)

        # Добавление образования
        education = Education.objects.create(
            student=profile,
            institution='Николаев',
            degree='Магистратура',
            start_date='2023-03-01',
            course_name='Менеджер проекта'
        )
        profile.educations.add(education)

        # Добавление опыта
        experience = Experience.objects.create(
            student=profile,
            title='Хакатон ТИ',
            description='Разработка бэкенда на Java.',
            start_date='2024-10-01'
        )
        profile.experiences.add(experience)

        # Добавление проекта
        project = Project.objects.create(
            student=profile,
            name='Проект на GitHub',
            url='https://github.com/roman',
            platform='github'
        )
        profile.projects.add(project)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))