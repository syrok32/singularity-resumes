from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student, StudentDetail
from  .serializers import StudentSerializer, StudentProfileSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.paginator import  Paginator
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
# Create your views here.
# views.py

from rest_framework import generics


class StudentList(generics.ListCreateAPIView):


    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'top_skills__name_skill']  # Фильтрация по роли и навыкам
    search_fields = ['full_name', 'short_description']  # Поиск по имени и описанию
    ordering_fields = ['full_name', 'role']
    permission_classes = [IsAuthenticatedOrReadOnly]

class StudentProfileDetail(generics.RetrieveAPIView):
    queryset = StudentDetail.objects.all()
    serializer_class = StudentProfileSerializer
