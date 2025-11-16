# telegram_bot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('applications/', views.create_application, name='create_application'),
    path('applications/<int:id>/status/', views.application_status, name='application_status'),
]
