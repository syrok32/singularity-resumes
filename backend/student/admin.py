from django.contrib import admin
from .models import Student, SkillCategory, Skill, Specialty, Education, WorkExperience, Portfolio, InternshipApplication


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class PortfolioInline(admin.TabularInline):
    model = Portfolio
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "is_active")
    list_filter = ("is_active", "city")
    search_fields = ("user__email", "user__username", "city")
    filter_horizontal = ("skills",)
    inlines = [EducationInline, WorkExperienceInline, PortfolioInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("skills",)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("student", "institution", "start_year", "end_year")
    search_fields = ("institution", "student__user__username")


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ("student", "position", "company", "start_date", "end_date")
    search_fields = ("position", "company", "student__user__username")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "link")
    search_fields = ("title", "student__user__username")


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "employer_name", "status", "student_response", "moderator_response", "created_at")
    list_filter = ("status", "student_response", "moderator_response")
    search_fields = ("student__user__email", "student__full_name", "employer_name", "message")
    readonly_fields = ("created_at", "updated_at")
