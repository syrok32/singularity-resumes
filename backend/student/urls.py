from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet
from .api_views import filter_options, student_stats
from telegram_bot.views import create_application

router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='profiles')

urlpatterns = [
    path('', include(router.urls)),
    path('filter-options/', filter_options, name='filter-options'),
    path('stats/', student_stats, name='student-stats'),
    path('applications/', create_application, name='create-application'),
    # path('telegram/webhook/<str:token>/', telegram_webhook)
]