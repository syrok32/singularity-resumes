
from django.contrib import admin
from .models import Student, Skill, StudentDetail


class StudentDetailInline(admin.StackedInline):
    model = StudentDetail
    extra = 0
    verbose_name = "Профиль студента"
    verbose_name_plural = "Профили студента"
    filter_horizontal = ('skills',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'profile_url')
    search_fields = ('full_name', 'role')
    list_filter = ('top_skills',)
    filter_horizontal = ('top_skills',)
    inlines = [StudentDetailInline]
    readonly_fields = ('photo_preview',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'role', 'top_skills', 'profile_url', 'short_description')
        }),
        ('Фото', {
            'fields': ('photo_url', 'photo_preview'),
        }),
    )

    def photo_preview(self, obj):
        if obj.photo_url:
            return f'<img src="{obj.photo_url.url}" style="max-height: 200px;" />'
        return "(Нет изображения)"
    photo_preview.short_description = 'Предпросмотр фото'
    photo_preview.allow_tags = True  # для старых версий Django


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name_skill',)
    search_fields = ('name_skill',)


@admin.register(StudentDetail)
class StudentDetailAdmin(admin.ModelAdmin):
    list_display = ('student', 'description',)
    search_fields = ('student__full_name', 'description',)
    filter_horizontal = ('skills',)
    readonly_fields = ('student',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('student', 'description', 'skills')
        }),
    )
