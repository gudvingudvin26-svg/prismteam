"""Маршрутизация URL приложения: админка, аутентификация, API квизов и сессий.

Настраивает Django URLconf:
• Перенаправление корня на API-панель организатора;
• Подключение Django Admin;
• Веб-маршруты для регистрации, входа, выхода и главной страницы;
• API-эндпоинты аутентификации (регистрация, логин, токен, профиль);
• DRF Router для CRUD-операций с квизами, вопросами, вариантами и сессиями;
• Включение дополнительных маршрутов сессий через include().

Все маршруты сгруппированы по функциональным областям для удобства
поддержки и расширения.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter

from app_modules.quiz.views import (
    UserRegistration, UserLogin, UserLogout, Main,
    QuizViewSet, QuestionViewSet, AnswerOptionViewSet,
    UserRegistrationAPI, UserLoginAPI, GetCurrentUserAPI, TokenRefreshAPI
)
from app_modules.quiz_sessions.views import QuizSessionViewSet

# DRF Router для автоматической генерации CRUD-маршрутов
router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerOptionViewSet, basename='answerooption')
router.register(r'sessions', QuizSessionViewSet, basename='session')

urlpatterns = [
    # Корень: редирект на панель организатора
    path('', lambda request: redirect('/api/organizer/quizzes/')),

    # Админ-панель Django
    path('admin/', admin.site.urls),

    # Веб-маршруты аутентификации и навигации
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('main/', Main.as_view(), name='main'),
    path('logout/', UserLogout.as_view(), name='logout'),

    # API-маршруты аутентификации
    path('api/auth/register/', UserRegistrationAPI.as_view(), name='api_register'),
    path('api/auth/login/', UserLoginAPI.as_view(), name='api_login'),
    path('api/auth/me/', GetCurrentUserAPI.as_view(), name='auth_me'),
    path('api/auth/refresh/', TokenRefreshAPI.as_view(), name='api_refresh'),

    # API-маршруты организатора (CRUD через DRF Router)
    path('api/organizer/', include(router.urls)),

    # Маршруты сессий (внешний include для модульности)
    path('api/sessions/join/', include('app_modules.quiz_sessions.urls')),
]