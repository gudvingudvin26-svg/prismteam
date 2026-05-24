from django.db import models
from app_modules.quiz.models import Quiz, Question, AnswerOption


class QuizSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    code = models.CharField(max_length=6, unique=True)
    participant_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'app_modules.quiz_sessions'

    def __str__(self):
        return f"{self.quiz.title} - {self.code} - {self.participant_name}"


class ParticipantAnswer(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'app_modules.quiz_sessions'

    def __str__(self):
        return f"{self.session.code} - Q{self.question.id}: {self.is_correct}"