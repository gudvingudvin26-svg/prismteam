import random
import string
from django.db import models
from django.contrib.auth.models import User


def generate_access_token(length=16):
    """
    Генерирует случайный токен из латинских букв, цифр и специальных символов.

    Args:
        length (int): Длина токена (по умолчанию 16 символа).

    Returns:
        str: Случайно сгенерированный токен.
    """
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(chars) for _ in range(length))


def generate_default_token():
    """
    Вспомогательная функция для генерации токена по умолчанию.

    Используется в поле access_token модели Quiz.
    """
    return generate_access_token(16)


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
        default=generate_default_token,
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
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        """Метаданные модели: сортировка по полю 'order'."""
        ordering = ['order']

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