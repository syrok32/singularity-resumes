from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet
from .api_views import filter_options, student_stats

router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='profiles')

urlpatterns = [
    path('', include(router.urls)),
    path('filter-options/', filter_options, name='filter-options'),
    path('stats/', student_stats, name='student-stats'),
]