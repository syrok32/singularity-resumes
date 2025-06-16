from django.contrib import admin
from .models import Student, StudentDetail, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name_skill',)
    search_fields = ('name_skill',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'photo_url')  # Добавили photo_url для отображения
    list_filter = ('role', 'top_skills')
    search_fields = ('full_name', 'role', 'short_description')
    filter_horizontal = ('top_skills',)

@admin.register(StudentDetail)
class StudentDetailAdmin(admin.ModelAdmin):
    list_display = ('student',)
    search_fields = ('student__full_name', 'description')
    filter_horizontal = ('skills',)
    autocomplete_fields = ['student', 'skills']