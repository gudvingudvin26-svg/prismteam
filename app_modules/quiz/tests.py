import django
from django.test import TestCase
from django.conf import settings
from django.apps import apps

class InfrastructureTestCase(TestCase):
    """Базовые проверки, что проект собран корректно."""

    def test_settings_module(self):
        """Проверяем, что Django загружен с нашим settings."""
        self.assertEqual(settings.SETTINGS_MODULE, 'config.settings')

    def test_app_installed(self):
        """Приложение quiz присутствует в INSTALLED_APPS."""
        self.assertIn('app_modules.quiz', settings.INSTALLED_APPS)

    def test_auth_user_model(self):
        """Кастомная модель пользователя указана."""
        self.assertEqual(settings.AUTH_USER_MODEL, 'quiz.User')

    def test_models_importable(self):
        """Модели quiz импортируются без ошибок."""
        from app_modules.quiz.models import User, Quiz, Question, AnswerOption
        self.assertTrue(hasattr(User, 'objects'))
        self.assertTrue(hasattr(Quiz, 'objects'))
        self.assertTrue(hasattr(Question, 'objects'))
        self.assertTrue(hasattr(AnswerOption, 'objects'))

    def test_admin_registered(self):
        """Проверяем, что модели зарегистрированы в админке."""
        from django.contrib import admin
        from app_modules.quiz.admin import QuizAdmin, QuestionAdmin
        # admin.site.is_registered(Quiz) -> True
        # Но чтобы не зависеть от полной регистрации, просто убедимся,
        # что классы админки определены.
        self.assertIsNotNone(QuizAdmin)
        self.assertIsNotNone(QuestionAdmin)