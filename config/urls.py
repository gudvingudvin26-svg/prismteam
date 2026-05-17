from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_modules.quiz.views import (
    UserRegistration, UserLogin, UserLogout, Main,
    QuizViewSet, QuestionViewSet, AnswerOptionViewSet
)

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerOptionViewSet, basename='answerooption')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth routes
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('main/', Main.as_view(), name='main'),
    path('logout/', UserLogout.as_view(), name='logout'),
    # Quiz API routes
    path('api/organizer/', include(router.urls)),
]
