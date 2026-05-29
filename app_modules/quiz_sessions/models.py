from django.db import models
from app_modules.quiz.models import Quiz, Question, AnswerOption

class QuizSession(models.Model):
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
        return f"{self.quiz.title} - {self.code} ({self.participant_name})"

class ParticipantAnswer(models.Model):
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
        return f"{self.session.code} - Q{self.question.id}: {self.is_correct}"