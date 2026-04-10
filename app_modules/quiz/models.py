"""Модели для приложения викторин."""

import secrets
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


def generate_token():
    """
    Вспомогательная функция для генерации токена по умолчанию.

    Используется в поле access_token модели Quiz.
    """
    return secrets.token_urlsafe(16)[:16]


class Quiz(models.Model):
    """
    Модель викторины.

    Содержит основную информацию о викторине, включая название, описание,
    создателя и уникальный токен доступа.
    """
    title = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Создатель"
    )
    access_token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_token,
        verbose_name="Токен доступа"
    )

    def __str__(self):
        """Возвращает строковое представление викторины."""
        return self.title


class Question(models.Model):
    """
    Модель вопроса.

    Представляет собой один вопрос викторины, принадлежащий конкретной викторине.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Викторина"
    )
    text = models.TextField(
        verbose_name="Текст вопроса",
        validators=[MinLengthValidator(5, message="Вопрос слишком короткий (минимум 5 символов)")],
        blank=False,
        null=False
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        """Метаданные модели: сортировка сначала по полю 'quiz', затем по полю 'order'."""
        ordering = ['quiz', 'order']

    def clean(self):
        """Проверяет, что текст вопроса не состоит только из пробелов."""
        if self.text and not self.text.strip():
            raise ValidationError({'text': "Текст вопроса не может состоять только из пробелов."})

    def __str__(self):
        """Возвращает строковое представление вопроса."""
        return f"{self.quiz.title} - {self.text[:50] if len(self.text) > 50 else self.text}"


class AnswerOption(models.Model):
    """
    Модель варианта ответа.

    Один из возможных ответов на вопрос. Может быть помечен как правильный.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=300, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        """Возвращает строковое представление варианта ответа."""
        status = '✓' if self.is_correct else '✗'
        return f"[{status}] {self.text}"