from unittest.mock import Mock

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app_modules.quiz.models import Quiz, Question, AnswerOption
from app_modules.quiz.observer import GameObserver
from app_modules.quiz.serializers import (
    QuizSerializer,
    QuestionSerializer,
    AnswerOptionSerializer
)
from app_modules.quiz_sessions.models import QuizSession
from app_modules.quiz.authentication import CookieJWTAuthentication

User = get_user_model()


class SerializerTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='test@test.com',
            password='12345678'
        )

        self.quiz = Quiz.objects.create(
            title='Quiz',
            created_by=self.user
        )

        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Question?',
            order=1,
            question_type='single'
        )

        self.answer = AnswerOption.objects.create(
            question=self.question,
            text='Answer',
            is_correct=True
        )

    def test_quiz_serializer(self):
        serializer = QuizSerializer(self.quiz)

        self.assertEqual(
            serializer.data['title'],
            'Quiz'
        )

    def test_question_serializer(self):
        serializer = QuestionSerializer(self.question)

        self.assertEqual(
            serializer.data['text'],
            'Question?'
        )

    def test_answer_serializer(self):
        serializer = AnswerOptionSerializer(self.answer)

        self.assertEqual(
            serializer.data['text'],
            'Answer'
        )


class ObserverTests(APITestCase):

    def test_subscribe_notify_unsubscribe(self):
        observer = GameObserver()

        callback = Mock()

        observer.subscribe('event', callback)

        observer.notify('event', value=123)

        callback.assert_called_once()

        observer.unsubscribe('event', callback)

        observer.notify('event', value=456)

        self.assertEqual(callback.call_count, 1)


class AuthenticationTests(APITestCase):

    def test_cookie_auth_no_token(self):
        auth = CookieJWTAuthentication()

        request = Mock()
        request.COOKIES = {}

        result = auth.authenticate(request)

        self.assertIsNone(result)


class SessionExtraTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='12345678'
        )

        self.client.force_authenticate(self.user)

        self.quiz = Quiz.objects.create(
            title='Quiz',
            created_by=self.user
        )

    def test_create_session_without_quiz(self):
        response = self.client.post(
            '/api/organizer/sessions/',
            {}
        )

        self.assertEqual(response.status_code, 400)

    def test_join_without_code(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            '/api/organizer/sessions/join/',
            {
                'nickname': 'player'
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_start_invalid_session(self):
        response = self.client.post(
            '/api/organizer/sessions/999/start/'
        )

        self.assertEqual(response.status_code, 404)

    def test_end_invalid_session(self):
        response = self.client.post(
            '/api/organizer/sessions/999/end/'
        )

        self.assertEqual(response.status_code, 404)

    def test_answer_invalid_session(self):
        response = self.client.post(
            '/api/organizer/sessions/999/answer/',
            {}
        )

        self.assertEqual(response.status_code, 404)

    def test_results_invalid_session(self):
        response = self.client.get(
            '/api/organizer/sessions/999/results/'
        )

        self.assertEqual(response.status_code, 404)

    def test_my_result_invalid_session(self):
        response = self.client.get(
            '/api/organizer/sessions/999/my_result/'
        )

        self.assertEqual(response.status_code, 404)

    def test_questions_stats_invalid_session(self):
        response = self.client.get(
            '/api/organizer/sessions/999/questions_stats/'
        )

        self.assertEqual(response.status_code, 200)

    def test_retrieve_invalid_session(self):
        response = self.client.get(
            '/api/organizer/sessions/999/'
        )

        self.assertEqual(response.status_code, 404)

    def test_retrieve_player_session(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player'
        )

        response = self.client.get(
            f'/api/organizer/sessions/{session.id}/'
        )

        self.assertIn(response.status_code, [200, 400])
