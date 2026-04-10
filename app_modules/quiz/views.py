"""ViewSet'ы для управления викторинами, вопросами и вариантами ответов."""

from django.db.models import Prefetch

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Quiz, Question, AnswerOption
from .serializers import QuizSerializer, QuestionSerializer, AnswerOptionSerializer
from .validators import validate_quiz_integrity


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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        """
        Метод для финальной публикации квиза.
        Запускает проверку целостности всех вопросов и ответов.
        """
        quiz = self.get_object()

        try:
            validate_quiz_integrity(quiz, use_drf_exception=True)

            # Если в модели Quiz появится поле status/is_published, обновляем его здесь:
            # quiz.is_published = True
            # quiz.save()

            return Response({"status": "Квиз успешно прошел валидацию и готов к публикации."},
                            status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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