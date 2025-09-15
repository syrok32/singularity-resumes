from django.core.management.base import BaseCommand
from django.db import transaction

from student.models import Specialty, Skill, SkillCategory


SPECIALTY_TO_CATEGORIES = {
    # Пример маппинга: "Специальность" → ["Категория навыков", ...]
    # Заполни/поправь под свой проект в админке при необходимости
    "Frontend": ["Frontend", "Web"],
    "Backend": ["Backend", "Databases"],
    "Data Science": ["Data Science", "ML", "Python"],
    "Mobile": ["Mobile", "Android", "iOS"],
    "DevOps": ["DevOps", "Cloud"],
}


class Command(BaseCommand):
    help = "Линкует навыки к специальностям по категориям (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Очистить связи перед линковкой")

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get("reset")

        if reset:
            self.stdout.write("Сбрасываю связи specialties ↔ skills...")
            for spec in Specialty.objects.all():
                spec.skills.clear()

        linked_total = 0
        for spec in Specialty.objects.all():
            categories = SPECIALTY_TO_CATEGORIES.get(spec.name, [])
            if not categories:
                # Хак: если точного маппинга нет — пробуем по совпадению названия
                # категории с частью названия специальности (case-insensitive)
                part = spec.name.lower()
                qs = Skill.objects.filter(category__name__icontains=part)
            else:
                qs = Skill.objects.filter(category__name__in=categories)

            skills = list(qs)
            if not skills:
                continue

            spec.skills.add(*skills)
            linked_total += len(skills)
            self.stdout.write(self.style.SUCCESS(f"Связал {len(skills)} навыков со специальностью '{spec.name}'"))

        self.stdout.write(self.style.SUCCESS(f"Готово. Всего связей: {linked_total}"))


