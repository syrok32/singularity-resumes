from .models import Student, StudentProfiles, Skill
from rest_framework import serializers
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name_skill']
class StudentSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    class Meta:
        model = Student
        fields = '__all__'

class StudentProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)

    class Meta:
        model = StudentProfiles
        fields = '__all__'
