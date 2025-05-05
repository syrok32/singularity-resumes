from django.urls import path

from .views import StudentList, StudentProfileDetail

urlpatterns = [
    path('api/students/', StudentList.as_view(), name='user-list'),
    path('student/detail/<int:pk>/', StudentProfileDetail.as_view(), name='student-profile-detail'),
]
