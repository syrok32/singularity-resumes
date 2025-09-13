import random
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import Skill, Student, StudentDetail

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Заполняет базу студентов и скиллов заглушками'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students', type=int, default=5, help='Количество студентов для создания'
        )
        parser.add_argument(
            '--skills', type=int, default=10, help='Количество скиллов для создания'
        )

    def handle(self, *args, **options):
        num_students = options['students']
        num_skills = options['skills']

        # 1. Создаём скиллы
        skills_list = []
        for _ in range(num_skills):
            skill_name = fake.job()[:50]  # берём случайную профессию
            skill, created = Skill.objects.get_or_create(name_skill=skill_name)
            skills_list.append(skill)

        self.stdout.write(self.style.SUCCESS(f'Создано {len(skills_list)} скиллов.'))

        # 2. Создаём студентов
        for _ in range(num_students):
            student = Student.objects.create(
                full_name=fake.name(),
                role=fake.job(),
                short_description=fake.text(max_nb_chars=200),
                profile_url=fake.url()
            )

            # Добавляем случайные топ-скиллы
            top_skills = random.sample(skills_list, k=min(3, len(skills_list)))
            student.top_skills.set(top_skills)

            # Создаём профиль студента
            detail = StudentDetail.objects.create(student=student)
            detail.skills.set(random.sample(skills_list, k=min(5, len(skills_list))))
            detail.description = fake.text(max_nb_chars=300)
            detail.save()

        self.stdout.write(self.style.SUCCESS(f'Создано {num_students} студентов с профилями.'))
