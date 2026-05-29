from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Неверный формат телефона')]
    )

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
    info = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def generate_token():
    return secrets.token_urlsafe(16)[:16]

class Quiz(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        db_index=True,
        validators=[MinLengthValidator(3)]
    )
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
        verbose_name="Токен доступа",
        db_index=True
    )
    timer = models.IntegerField(blank=True, null=True, verbose_name="Таймер в секундах")
    points_per_question = models.IntegerField(default=100, verbose_name="Баллов за правильный ответ")

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single', 'Одиночный выбор'),
        ('multiple', 'Множественный выбор'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Викторина"
    )
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='single',
        verbose_name="Тип вопроса"
    )
    timer = models.IntegerField(blank=True, null=True, verbose_name="Таймер на вопрос в секундах")
    points = models.IntegerField(default=100, verbose_name="Баллов за правильный ответ")

    class Meta:
        ordering = ['quiz', 'order']

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"

class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=500, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f"[{status}] {self.text}"