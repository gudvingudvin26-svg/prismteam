import django
from django.test import TestCase
from django.conf import settings
from django.apps import apps

class InfrastructureTestCase(TestCase):
    """Проверки корректности настройки проекта в devops-ветке."""

    def test_settings_module(self):
        """Django загружен с правильным модулем настроек."""
        self.assertEqual(settings.SETTINGS_MODULE, 'config.settings')

    def test_app_installed(self):
        """Приложение quiz присутствует в INSTALLED_APPS."""
        self.assertIn('app_modules.quiz', settings.INSTALLED_APPS)

    def test_auth_user_model_default(self):
        """Используется стандартная модель User."""
        self.assertEqual(settings.AUTH_USER_MODEL, 'auth.User')

    def test_models_module_importable(self):
        """Модуль models.py импортируется без ошибок."""
        try:
            import app_modules.quiz.models as models_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.models")
        self.assertIsNotNone(models_module)

    def test_admin_module_importable(self):
        """Модуль admin.py импортируется без ошибок."""
        try:
            import app_modules.quiz.admin as admin_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.admin")
        self.assertIsNotNone(admin_module)