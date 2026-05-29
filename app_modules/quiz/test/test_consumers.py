from django.test import TestCase
from app_modules.quiz.consumers import QuizConsumer


class ConsumerUnitTests(TestCase):

    def test_get_leaderboard_data(self):
        consumer = QuizConsumer()

        consumer.user_scores = {
            'alice': 300,
            'bob': 100,
            'charlie': 200
        }

        data = consumer._get_leaderboard_data()

        self.assertEqual(data[0]['participant_name'], 'alice')
        self.assertEqual(data[0]['score'], 300)

    def test_get_display_name_anonymous(self):
        consumer = QuizConsumer()

        consumer.scope = {}
        consumer.channel_name = 'abcdef123456'

        name = consumer._get_display_name()

        self.assertTrue(name.startswith('User_'))

    def test_get_display_name_authenticated(self):
        class User:
            is_authenticated = True
            username = 'tester'

        consumer = QuizConsumer()
        consumer.scope = {'user': User()}

        self.assertEqual(
            consumer._get_display_name(),
            'tester'
        )
