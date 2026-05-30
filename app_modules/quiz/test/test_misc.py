from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from app_modules.quiz.authentication import CookieJWTAuthentication
from app_modules.quiz.middleware import CORSMiddleware
from app_modules.quiz.observer import GameObserver
from app_modules.quiz.redis_utils import RedisTimerManager, get_timer_manager

User = get_user_model()


class MiddlewareTests(TestCase):

    def test_middleware_call(self):
        request = Mock()

        response_mock = Mock(return_value='response')

        middleware = CORSMiddleware(response_mock)

        response = middleware(request)

        self.assertEqual(response, 'response')
        response_mock.assert_called_once()


class AuthenticationMoreTests(TestCase):

    def test_authenticate_invalid_token(self):
        auth = CookieJWTAuthentication()

        request = Mock()
        request.COOKIES = {
            'access_token': 'invalid'
        }

        result = auth.authenticate(request)

        self.assertIsNone(result)

    def test_authenticate_header(self):
        auth = CookieJWTAuthentication()

        request = Mock()
        request.COOKIES = {}

        result = auth.authenticate_header(request)

        self.assertEqual(result, 'Bearer')


class ObserverMoreTests(TestCase):

    def test_unsubscribe_missing_event(self):
        observer = GameObserver()

        callback = Mock()

        observer.unsubscribe('missing', callback)

        self.assertEqual(observer._observers, {})


class RedisUtilsTests(TestCase):

    def test_timer_manager_singleton(self):
        tm1 = get_timer_manager()
        tm2 = get_timer_manager()

        self.assertEqual(tm1, tm2)

    def test_start_question_timer(self):
        manager = RedisTimerManager()

        manager.start_question_timer(
            quiz_id='1',
            question_number=1,
            duration=30
        )

        result = manager.get_question_timer('1', 1)

        self.assertTrue(result['remaining'] <= 30)

    def test_get_time_remaining(self):
        manager = RedisTimerManager()

        manager.start_question_timer(
            quiz_id='1',
            question_number=1,
            duration=30
        )

        remaining = manager.get_time_remaining('1', 1)

        self.assertTrue(remaining <= 30)

    def test_get_time_remaining_missing(self):
        manager = RedisTimerManager()

        remaining = manager.get_time_remaining('999', 1)

        self.assertEqual(remaining, 0)

    def test_get_question_timer_missing(self):
        manager = RedisTimerManager()

        result = manager.get_question_timer('999', 1)

        self.assertEqual(result, {})


class RoutingImportTests(TestCase):

    def test_import_routing(self):
        import app_modules.quiz.routing

        self.assertIsNotNone(app_modules.quiz.routing)
