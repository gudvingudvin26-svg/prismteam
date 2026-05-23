import django
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.contrib import auth
from django.apps import apps

from .models import User


# ========== ТЕСТЫ АУТЕНТИФИКАЦИИ ==========
class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create(username="Just_random_user", email="just.random_user@gmail.com", phone='7123456789', password="1234")

    def test_get(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_right_login_by_username(self):
        self.client.post(reverse('login'), {'identification_parameter': 'Just_random_user', 'password': "1234"})
        user = auth.get_user(self.client)
        assert user.is_authenticated

    def test_right_login_by_email(self):
        self.client.post(reverse('login'), {'identification_parameter': 'just.random_user@gmail.com', 'password': "1234"})
        user = auth.get_user(self.client)
        assert user.is_authenticated

    def test_right_login_by_phone(self):
        self.client.post(reverse('login'), {'identification_parameter': '7123456789', 'password': "1234"})
        user = auth.get_user(self.client)
        assert user.is_authenticated

    def test_wrong_password(self):
        self.client.post(reverse('login'), {'identification_parameter': 'just.random_user@gmail.com', 'password': "12345"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    def test_wrong_ident_par(self):
        self.client.post(reverse('login'), {'identification_parameter': 'just.random_user@gmail.comm', 'password': "1234"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated


class TestRegistration(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        self.assertEqual(self.client.get(reverse('registration')).status_code, 200)

    def test_right_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user', 'email': "just.random_user@gmail.com", 'phone': '7123456789', 'password': "1234", 'again_password': "1234"})
        user = auth.get_user(self.client)
        assert user.is_authenticated

    def test_not_same_passwords_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user', 'email': "just.random_user@gmail.com", 'phone': '7123456789', 'password': "1234", 'again_password': "12345"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    def test_big_phone_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user', 'email': "just.random_user@gmail.com", 'phone': '712345678999999999', 'password': "1234", 'again_password': "1234"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    def test_small_phone_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user', 'email': "just.random_user@gmail.com", 'phone': '7123', 'password': "1234", 'again_password': "1234"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    def test_wrong_email_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user', 'email': "just.random_user_gmail.com", 'phone': '7123456789', 'password': "1234", 'again_password': "1234"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    def test_dog_in_the_username_registration(self):
        self.client.post(reverse('registration'), {'username': 'Just_random_user@', 'email': "just.random_user@gmail.com", 'phone': '7123456789', 'password': "1234", 'again_password': "1234"})
        user = auth.get_user(self.client)
        assert not user.is_authenticated


class TestLogout(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create(username="Just_random_user", email="just.random_user@gmail.com", phone='7123456789', password="1234")

    def test_get(self):
        self.assertEqual(self.client.get(reverse('logout')).status_code, 302)

    def test_logout(self):
        self.client.post(reverse('logout'), {})
        user = auth.get_user(self.client)
        assert not user.is_authenticated


class InfrastructureTestCase(TestCase):

    def test_settings_module(self):
        self.assertEqual(settings.SETTINGS_MODULE, 'config.settings')

    def test_app_installed(self):
        self.assertIn('app_modules.quiz', settings.INSTALLED_APPS)

    def test_auth_user_model_custom(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'quiz.User')

    def test_models_module_importable(self):
        try:
            import app_modules.quiz.models as models_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.models")
        self.assertIsNotNone(models_module)

    def test_admin_module_importable(self):
        try:
            import app_modules.quiz.admin as admin_module
        except ImportError:
            self.fail("Не удалось импортировать app_modules.quiz.admin")
        self.assertIsNotNone(admin_module)