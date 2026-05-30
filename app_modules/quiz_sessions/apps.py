"""Конфигурация Django-приложения для управления сессиями квизов."""
from django.apps import AppConfig


class QuizSessionsConfig(AppConfig):
    """Конфигурация приложения сессий: путь, метка и параметры БД.

    Регистрирует приложение в Django, задаёт тип автоинкрементных полей
    и уникальную метку для предотвращения конфликтов моделей при миграциях.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_modules.quiz_sessions'
    label = 'quiz_sessions'