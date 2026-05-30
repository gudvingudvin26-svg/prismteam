from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from app_modules.quiz.models import Quiz, Question, AnswerOption
from app_modules.quiz_sessions.models import QuizSession, ParticipantAnswer

User = get_user_model()


class AuthTests(APITestCase):

    def test_register_api_success(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'tester',
            'email': 'test@test.com',
            'password': 'strongpass123',
            'again_password': 'strongpass123'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_register_api_password_mismatch(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'tester',
            'email': 'test@test.com',
            'password': '123456',
            'again_password': '654321'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_success(self):
        user = User.objects.create_user(
            username='tester',
            email='test@test.com',
            password='12345678'
        )

        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': '12345678'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_api_wrong_password(self):
        user = User.objects.create_user(
            username='tester',
            email='test@test.com',
            password='12345678'
        )

        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'wrong'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class QuizTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='12345678'
        )

        self.client.force_authenticate(self.user)

    def test_create_quiz(self):
        response = self.client.post('/api/organizer/quizzes/', {
            'title': 'Math Quiz',
            'description': 'Test'
        })

        self.assertIn(response.status_code, [200, 201])

    def test_get_quizzes(self):
        Quiz.objects.create(
            title='Quiz 1',
            created_by=self.user
        )

        response = self.client.get('/api/organizer/quizzes/')

        self.assertEqual(response.status_code, 200)

    def test_delete_quiz(self):
        quiz = Quiz.objects.create(
            title='Quiz',
            created_by=self.user
        )

        response = self.client.delete(
            f'/api/organizer/quizzes/{quiz.id}/'
        )

        self.assertEqual(response.status_code, 204)

    def test_publish_quiz_not_found(self):
        response = self.client.post(
            '/api/organizer/quizzes/999/publish/'
        )

        self.assertEqual(response.status_code, 404)


class SessionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='12345678'
        )

        self.client.force_authenticate(self.user)

        self.quiz = Quiz.objects.create(
            title='Quiz',
            created_by=self.user,
            timer=30
        )

        self.question = Question.objects.create(
            quiz=self.quiz,
            text='2+2?',
            question_type='single',
            order=1,
            points=100
        )

        self.correct_answer = AnswerOption.objects.create(
            question=self.question,
            text='4',
            is_correct=True
        )

        self.wrong_answer = AnswerOption.objects.create(
            question=self.question,
            text='5',
            is_correct=False
        )

    def test_create_session(self):
        response = self.client.post('/api/organizer/sessions/', {
            'quiz': self.quiz.id
        })

        self.assertEqual(response.status_code, 201)

    def test_join_session(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            status='waiting'
        )

        self.client.force_authenticate(user=None)

        response = self.client.post(
            '/api/organizer/sessions/join/',
            {
                'code': '123456',
                'nickname': 'player1'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_start_session(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456'
        )

        response = self.client.post(
            f'/api/organizer/sessions/{session.id}/start/'
        )

        self.assertEqual(response.status_code, 200)

    def test_end_session(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456'
        )

        response = self.client.post(
            f'/api/organizer/sessions/{session.id}/end/'
        )

        self.assertEqual(response.status_code, 200)

    def test_answer_correct(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player'
        )

        self.client.force_authenticate(user=None)

        response = self.client.post(
            f'/api/organizer/sessions/{session.id}/answer/',
            {
                'question_id': self.question.id,
                'answer_id': self.correct_answer.id
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_correct'])

    def test_answer_wrong(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player'
        )

        self.client.force_authenticate(user=None)

        response = self.client.post(
            f'/api/organizer/sessions/{session.id}/answer/',
            {
                'question_id': self.question.id,
                'answer_id': self.wrong_answer.id
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_correct'])

    def test_results(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player'
        )

        ParticipantAnswer.objects.create(
            session=session,
            question=self.question,
            answer=self.correct_answer,
            is_correct=True
        )

        response = self.client.get(
            f'/api/organizer/sessions/{session.id}/results/'
        )

        self.assertEqual(response.status_code, 200)

    def test_my_result(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player'
        )

        ParticipantAnswer.objects.create(
            session=session,
            question=self.question,
            answer=self.correct_answer,
            is_correct=True
        )

        response = self.client.get(
            f'/api/organizer/sessions/{session.id}/my_result/'
        )

        self.assertEqual(response.status_code, 200)

    def test_questions_stats(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            code='123456',
            participant_name='player',
            status='completed'
        )

        ParticipantAnswer.objects.create(
            session=session,
            question=self.question,
            answer=self.correct_answer,
            is_correct=True
        )

        response = self.client.get(
            f'/api/organizer/sessions/{session.id}/questions_stats/'
        )

        self.assertEqual(response.status_code, 200)
