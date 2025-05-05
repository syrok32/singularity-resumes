from django.shortcuts import render

from .models import Student, StudentDetail
from  .serializers import StudentSerializer, StudentProfileSerializer

# Create your views here.
# views.py

from rest_framework import generics


class StudentList(generics.ListCreateAPIView):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentProfileDetail(generics.RetrieveAPIView):
    queryset = StudentDetail.objects.all()
    serializer_class = StudentProfileSerializer
