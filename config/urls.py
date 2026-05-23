from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_modules.quiz.views import (
    UserRegistration, UserLogin, UserLogout, Main,
    QuizViewSet, QuestionViewSet, AnswerOptionViewSet,
    UserRegistrationAPI, UserLoginAPI
)
from app_modules.quiz_sessions.views import QuizSessionViewSet

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerOptionViewSet, basename='answerooption')
router.register(r'sessions', QuizSessionViewSet, basename='session')  # ← добавить

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('main/', Main.as_view(), name='main'),
    path('logout/', UserLogout.as_view(), name='logout'),

    path('auth/register/', UserRegistrationAPI.as_view(), name='auth_register'),
    path('auth/login/', UserLoginAPI.as_view(), name='auth_login'),
    path('api/auth/login/', UserLoginAPI.as_view(), name='api_login'),
    path('api/auth/register/', UserRegistrationAPI.as_view(), name='api_register'),
    path('api/organizer/', include(router.urls)),
]