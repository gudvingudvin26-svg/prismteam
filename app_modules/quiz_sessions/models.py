"""Модели сессий квизов: отслеживание прохождений, статусов и ответов участников."""
from django.db import models
from app_modules.quiz.models import Quiz, Question, AnswerOption


class QuizSession(models.Model):
    """Модель сессии прохождения квиза: управление статусом, кодом доступа и временными метками.

    Хранит данные о конкретном прохождении квиза:
    • code — короткий уникальный код для быстрого подключения;
    • status — жизненный цикл сессии (ожидание, активна, завершена);
    • временные метки создания, старта и завершения;
    • флаг is_completed для оптимизации запросов и обеспечения уникальности.

    Мета-данные:
    • unique_together гарантирует одну незавершённую сессию на пару (квиз, участник);
    • Индекс по (code, status) ускоряет поиск и фильтрацию активных сессий.
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    code = models.CharField(max_length=10, db_index=True)
    participant_name = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_session'
        indexes = [
            models.Index(fields=['code', 'status']),
        ]
        unique_together = [['quiz', 'participant_name', 'is_completed']]

    def __str__(self):
        """Строковое представление: название квиза, код сессии и имя участника."""
        return f"{self.quiz.title} - {self.code} ({self.participant_name})"


class ParticipantAnswer(models.Model):
    """Модель ответа участника: привязка к сессии, вопросу и выбранному варианту.

    Фиксирует результат ответа в рамках конкретной сессии:
    • answer — выбранный вариант (допускает null для пропущенных вопросов);
    • is_correct — флаг правильности ответа, вычисляемый при проверке;
    • answered_at — точное время отправки ответа для анализа скорости.

    Мета-данные:
    • Индекс по (session, question) оптимизирует загрузку прогресса и подсчёт баллов.
    """
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'participant_answer'
        indexes = [
            models.Index(fields=['session', 'question']),
        ]

    def __str__(self):
        """Строковое представление: код сессии, ID вопроса и результат проверки."""
        return f"{self.session.code} - Q{self.question.id}: {self.is_correct}"