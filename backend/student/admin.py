from django.contrib import admin
from .models import Student, Skill, StudentProfiles


class StudentProfilesInline(admin.StackedInline):
    model = StudentProfiles
    extra = 0
    verbose_name = "Профиль студента"
    verbose_name_plural = "Профили студента"


@admin.register(Student)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'profile_url')
    search_fields = ('full_name', 'role')
    list_filter = ('skills',)
    filter_horizontal = ('skills',)
    inlines = [StudentProfilesInline]
    readonly_fields = ('photo_preview',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'role', 'skills', 'resume_url', 'profile_url')
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


@admin.register(StudentProfiles)
class StudentProfilesAdmin(admin.ModelAdmin):
    list_display = ('student', 'resume_url', 'email', 'telegram', 'relocation_ready')
    search_fields = ('student__full_name', 'email', 'telegram')
    list_filter = ('relocation_ready',)
    filter_horizontal = ('skills',)
    readonly_fields = ('student',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('student', 'description', 'about', 'skills')
        }),
        ('Образование и опыт', {
            'fields': ('education', 'experience', 'projects')
        }),
        ('Контакты и соцсети', {
            'fields': ('email', 'telegram', 'phone', 'socials')
        }),
        ('Переезд', {
            'fields': ('relocation_ready', 'relocation_city')
        }),
    )
