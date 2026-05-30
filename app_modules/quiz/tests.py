"""Тесты аутентификации и инфраструктуры Django-приложения."""
import django
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.contrib import auth
from django.apps import apps
from .models import User


class TestLogin(TestCase):
    """Тесты входа пользователя по username/email."""

    def setUp(self):
        """Создание тестового клиента и пользователя."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="Just_random_user",
            email="just.random_user@gmail.com",
            password="1234"
        )

    def test_get(self):
        """GET /login: возврат страницы входа с кодом 200."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_right_login_by_username(self):
        """POST /login: успешный вход по username."""
        response = self.client.post(reverse('login'), {
            'identification_parameter': 'Just_random_user',
            'password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_right_login_by_email(self):
        """POST /login: успешный вход по email."""
        response = self.client.post(reverse('login'), {
            'identification_parameter': 'just.random_user@gmail.com',
            'password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_password(self):
        """POST /login: отказ при неверном пароле."""
        response = self.client.post(reverse('login'), {
            'identification_parameter': 'just.random_user@gmail.com',
            'password': "12345"
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_wrong_ident_par(self):
        """POST /login: отказ при несуществующем идентификаторе."""
        response = self.client.post(reverse('login'), {
            'identification_parameter': 'just.random_user@gmail.comm',
            'password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class TestRegistration(TestCase):
    """Тесты регистрации нового пользователя."""

    def setUp(self):
        """Создание тестового клиента."""
        self.client = Client()

    def test_get(self):
        """GET /registration: возврат страницы регистрации с кодом 200."""
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_right_registration(self):
        """POST /registration: успешная регистрация с авторизацией."""
        response = self.client.post(reverse('registration'), {
            'username': 'Just_random_user',
            'email': "just.random_user@gmail.com",
            'password': "1234",
            'again_password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_not_same_passwords_registration(self):
        """POST /registration: отказ при несовпадении паролей."""
        response = self.client.post(reverse('registration'), {
            'username': 'Just_random_user',
            'email': "just.random_user@gmail.com",
            'password': "1234",
            'again_password': "12345"
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_wrong_email_registration(self):
        """POST /registration: отказ при невалидном email."""
        response = self.client.post(reverse('registration'), {
            'username': 'Just_random_user',
            'email': "just.random_user_gmail.com",
            'password': "1234",
            'again_password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_dog_in_the_username_registration(self):
        """POST /registration: отказ при наличии @ в username."""
        response = self.client.post(reverse('registration'), {
            'username': 'Just_random_user@',
            'email': "just.random_user@gmail.com",
            'password': "1234",
            'again_password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class TestLogout(TestCase):
    """Тесты выхода пользователя из системы."""

    def setUp(self):
        """Создание клиента и тестового пользователя."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="Just_random_user",
            email="just.random_user@gmail.com",
            password="1234"
        )

    def test_get(self):
        """GET /logout: возврат ответа с кодом 200."""
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """POST /logout: успешный выход и деаутентификация."""
        self.client.post(reverse('login'), {
            'identification_parameter': 'Just_random_user',
            'password': "1234"
        })
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.post(reverse('logout'), {})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class InfrastructureTestCase(TestCase):
    """Тесты конфигурации и инфраструктуры приложения."""

    def test_settings_module(self):
        """Проверка корректного модуля настроек Django."""
        self.assertEqual(settings.SETTINGS_MODULE, 'config.settings')

    def test_app_installed(self):
        """Проверка наличия приложения в INSTALLED_APPS."""
        self.assertIn('app_modules.quiz', settings.INSTALLED_APPS)

    def test_auth_user_model_custom(self):
        """Проверка использования кастомной модели пользователя."""
        self.assertEqual(settings.AUTH_USER_MODEL, 'quiz.User')

    def test_models_module_importable(self):
        """Проверка импортируемости модуля models."""
        try:
            import app_modules.quiz.models as models_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.models")
        self.assertIsNotNone(models_module)

    def test_admin_module_importable(self):
        """Проверка импортируемости модуля admin."""
        try:
            import app_modules.quiz.admin as admin_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.admin")
        self.assertIsNotNone(admin_module)