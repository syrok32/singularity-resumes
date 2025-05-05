from .models import Student, StudentDetail, Skill
from rest_framework import serializers
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name_skill']

class StudentSerializer(serializers.ModelSerializer):
    top_skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name_skill'
    )

    class Meta:
        model = Student
        fields = '__all__'
class StudentProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)

    class Meta:
        model = StudentDetail
        fields = '__all__'
