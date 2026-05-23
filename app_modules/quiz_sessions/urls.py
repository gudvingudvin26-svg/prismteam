from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizSessionViewSet

router = DefaultRouter()
router.register(r'sessions', QuizSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]