import django
from django.test import TestCase
from django.conf import settings
from django.apps import apps

class InfrastructureTestCase(TestCase):
    """Проверки работоспособности проекта в devops-ветке."""

    def test_settings_module(self):
        """Проверяем, что Django загружен с корректным settings."""
        self.assertEqual(settings.SETTINGS_MODULE, 'config.settings')

    def test_app_installed(self):
        """Приложение quiz присутствует в INSTALLED_APPS."""
        self.assertIn('app_modules.quiz', settings.INSTALLED_APPS)

    def test_auth_user_model_default(self):
        """В этой ветке используется стандартная модель User."""
        self.assertEqual(settings.AUTH_USER_MODEL, 'auth.User')

    def test_models_importable(self):
        """Любая модель quiz успешно импортируется."""
        from app_modules.quiz.models import Question
        self.assertTrue(hasattr(Question, 'objects'))

    def test_admin_importable(self):
        """Модуль admin.py импортируется без ошибок."""
        from app_modules.quiz import admin
        self.assertTrue(hasattr(admin, 'site'))