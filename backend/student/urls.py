from django.conf.urls.static import static
from django.urls import path

from .views import StudentList, StudentProfileDetail
from django.conf import settings

urlpatterns = [
    path('api/students/', StudentList.as_view(), name='user-list'),
    path('api/student/<int:pk>/', StudentProfileDetail.as_view(), name='student-profile-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
