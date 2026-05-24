import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13, blank=True, null=True, unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='quiz_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='quiz_user_set',
        blank=True,
    )

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    info = models.TextField(max_length=600, blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def generate_token():
    return secrets.token_urlsafe(16)[:16]


class Quiz(models.Model):
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
        return self.title


class Question(models.Model):
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
        ordering = ['quiz', 'order']

    def clean(self):
        if self.text and not self.text.strip():
            raise ValidationError({'text': "Текст вопроса не может состоять только из пробелов."})

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50] if len(self.text) > 50 else self.text}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=300, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f"[{status}] {self.text}"