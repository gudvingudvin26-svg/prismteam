from rest_framework import viewsets, permissions
from django.db.models import Prefetch
from .models import Quiz, Question, AnswerOption
from .serializers import QuizSerializer, QuestionSerializer, AnswerOptionSerializer


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления викторинами (CRUD).

    Обеспечивает изоляцию данных: пользователь видит и редактирует только свои викторины.
    Включает оптимизацию запросов для корректного отображения вложенных вопросов и ответов.
    """
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает викторины текущего пользователя с предзагрузкой связанных данных."""
        user = self.request.user
        return Quiz.objects.filter(
            created_by=user
        ).prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.select_related('quiz').prefetch_related('answer_options')
            )
        ).select_related('created_by').order_by('-id')

    def perform_create(self, serializer):
        """Сохраняет викторину, автоматически устанавливая текущего пользователя создателем."""
        serializer.save(created_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления вопросами (CRUD).

    Позволяет работать только с вопросами, принадлежащими викторинам текущего пользователя.
    Оптимизирован для загрузки вариантов ответов.
    """
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает вопросы из викторин текущего пользователя."""
        user = self.request.user
        return Question.objects.filter(
            quiz__created_by=user
        ).select_related('quiz').prefetch_related('answer_options')


class AnswerOptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления вариантами ответов (CRUD).

    Доступ ограничен ответами, которые принадлежат вопросам из викторин текущего пользователя.
    """
    serializer_class = AnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает варианты ответов, принадлежащие вопросам викторин текущего пользователя."""
        user = self.request.user
        return AnswerOption.objects.filter(
            question__quiz__created_by=user
        ).select_related('question__quiz')