"""
URL маршруты для приложения student.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudentProfileViewSet
from .api_views import filter_options

# Настройка роутера для ViewSet
router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='student-profiles')

# URL patterns
urlpatterns = [
    # ViewSet endpoints (автоматически генерируются роутером):
    # GET /profiles/ - список студентов
    # GET /profiles/{id}/ - детальный профиль
    # GET /profiles/top/ - топ-студенты для главной
    # GET /profiles/filter_options/ - опции фильтров
    # GET /profiles/stats/ - статистика
    path('', include(router.urls)),

    # Дополнительные endpoints для фильтров и статистики
    # (дублируются для обратной совместимости)
    path('filter-options/', filter_options, name='student-filter-options'),
]

# Итоговые URL для приложения student:
# /api/students/profiles/
# /api/students/profiles/{id}/
# /api/students/profiles/top/
# /api/students/profiles/filter_options/
# /api/students/profiles/stats/
# /api/students/filter-options/
# /api/students/stats/
