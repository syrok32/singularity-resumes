import base64

from .models import Student, StudentDetail, Skill
from rest_framework import serializers

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name_skill']

class StudentSerializer(serializers.ModelSerializer):
    top_skills = serializers.SerializerMethodField()
    photo_url = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'role', 'top_skills', 'short_description', 'photo_url', 'profile_url']

    def get_top_skills(self, obj):
        # Извлекаем только названия навыков
        return [skill.name_skill for skill in obj.top_skills.all()]


class StudentProfileSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    student_role = serializers.CharField(source='student.role', read_only=True)
    student_photo_url = serializers.ImageField(source='student.photo_url', read_only=True)
    student_profile_url = serializers.URLField(source='student.profile_url', read_only=True)
    student_top_skills = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = StudentDetail
        fields = ['id', 'student_full_name', 'student_role', 'student_photo_url', 'student_profile_url', 'student_top_skills', 'skills', 'description']

    def get_student_top_skills(self, obj):
        # Возвращаем только список названий top_skills
        return [skill.name_skill for skill in obj.student.top_skills.all()]

    def get_skills(self, obj):
        # Возвращаем только список названий skills
        return [skill.name_skill for skill in obj.skills.all()]