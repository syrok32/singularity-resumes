from django.shortcuts import render

from .models import Student, StudentProfiles
from  .serializers import StudentSerializer, StudentProfileSerializer

# Create your views here.
# views.py
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

class StudentList(generics.ListCreateAPIView):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentProfileDetail(generics.RetrieveAPIView):
    queryset = StudentProfiles.objects.all()
    serializer_class = StudentProfileSerializer
