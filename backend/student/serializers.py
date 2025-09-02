from rest_framework import serializers
from .models import Skill, SkillCategory, Specialty, Education, WorkExperience, Portfolio, Student


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    category = SkillCategorySerializer(read_only=True)

    class Meta:
        model = Skill
        fields = ["id", "name", "category"]


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ["id", "name"]


class EducationSerializer(serializers.ModelSerializer):
    specialty = SpecialtySerializer(read_only=True)

    class Meta:
        model = Education
        fields = ["id", "institution", "specialty", "start_year", "end_year", "additional_info"]


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ["id", "position", "company", "start_date", "end_date", "description"]


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "title", "link", "description"]


class StudentProfileSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    specialty = serializers.SerializerMethodField()
    educations = EducationSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "avatar_url",
            "birth_date",
            "phone_number",
            "email",
            "course",
            "bio",
            "city",
            "hh_link",
            "is_active",
            "skills",
            "specialty",
            "educations",
            "work_experiences",
            "portfolios",
        ]

    def get_skills(self, obj: Student):
        return [skill.name for skill in obj.skills.all()]

    def get_specialty(self, obj: Student):
        return obj.specialty.name if obj.specialty else None


class StudentCardSerializer(serializers.ModelSerializer):
    specialty = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "avatar_url",
            "course",
            "specialty",
            "skills",
            "description",
        ]

    def get_skills(self, obj: Student):
        top_five = obj.skills.all()[:5]
        return [skill.name for skill in top_five]

    def get_specialty(self, obj: Student):
        return obj.specialty.name if obj.specialty else None

    def get_description(self, obj: Student):
        if not obj.bio:
            return ""
        text = obj.bio.strip()
        return text if len(text) <= 100 else text[:100].rstrip() + '…'

