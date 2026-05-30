"""Модели данных приложения квизов.

Содержит определения основных сущностей: кастомная модель пользователя,
профиль пользователя, квизы, вопросы и варианты ответов. Включает сигналы
для автоматического создания профилей и утилиты генерации токенов доступа.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets


class User(AbstractUser):
    """Кастомная модель пользователя, расширяющая стандартную AbstractUser.

    Добавлены поля email (уникальный) и phone с валидацией международного формата.
    Переопределены связи ManyToMany для групп и разрешений, чтобы избежать
    конфликтов имён обратных связей (related_name) при подключении нескольких приложений.
    """
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
        """Возвращает строковое представление пользователя (логин)."""
        return self.username


class Profile(models.Model):
    """Расширенный профиль пользователя, связанный один-к-одному с User.

    Хранит дополнительную пользовательскую информацию (поле info).
    Использует user как primary_key, что позволяет обращаться к профилю
    напрямую через экземпляр пользователя (user.profile).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    info = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        """Возвращает читаемое представление профиля с указанием username."""
        return f'Profile of {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Сигнал-обработчик для автоматического создания профиля при регистрации.

    Срабатывает после сохранения экземпляра User. Если объект создан впервые
    (created=True), автоматически генерирует связанный Profile.

    Args:
        sender: Модель-отправитель сигнала (User).
        instance: Сохранённый экземпляр пользователя.
        created: Флаг, указывающий, был ли объект создан, а не обновлён.
        **kwargs: Дополнительные параметры сигнала Django.
    """
    if created:
        Profile.objects.create(user=instance)


def generate_token():
    """Генерирует уникальный URL-безопасный токен доступа.

    Использует криптографически стойкий генератор случайных чисел.
    Результат обрезается до 16 символов для компактного хранения в БД
    и удобства передачи в клиентских запросах.

    Returns:
        str: Уникальный строковый токен длиной 16 символов.
    """
    return secrets.token_urlsafe(16)[:16]


class Quiz(models.Model):
    """Модель квиза (викторины) с настройками доступа, времени и начисления баллов.

    Связана с создателем (User) через ForeignKey с каскадным удалением.
    Каждый квиз автоматически получает уникальный access_token для публичного доступа.
    Поддерживает глобальный таймер и базовые баллы за правильный ответ.
    """
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
        """Возвращает название квиза для отображения в админке и отладке."""
        return self.title


class Question(models.Model):
    """Модель вопроса, принадлежащего конкретному квизу.

    Поддерживает два типа вопросов: одиночный (single) и множественный (multiple) выбор.
    Содержит собственный таймер, порядок отображения (order) и переопределяемую
    систему баллов. Удаляется каскадно вместе с родительским квизом.
    """
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
        """Возвращает название квиза и первые 50 символов текста вопроса."""
        return f"{self.quiz.title} - {self.text[:50]}"


class AnswerOption(models.Model):
    """Модель варианта ответа на вопрос.

    Связана с Question каскадным удалением. Каждый вариант содержит текст
    и флаг правильности (is_correct). Валидация на уровне бизнес-логики
    гарантирует наличие минимум двух вариантов и корректное количество правильных ответов.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=500, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        """Возвращает текст ответа с визуальным маркером правильности (✓/✗)."""
        status = '✓' if self.is_correct else '✗'
        return f"[{status}] {self.text}"