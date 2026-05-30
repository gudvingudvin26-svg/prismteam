import uuid

from django.test import TestCase

from app_modules.quiz.models import (
    User,
    Quiz,
    Question,
)

from app_modules.quiz.serializers import (
    QuizSerializer,
    QuestionSerializer,
)


class SerializerExtendedTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="serializer",
            email=f"serializer_{uuid.uuid4()}@mail.com",
            password="pass123"
        )

        self.quiz = Quiz.objects.create(
            title="Serializer Quiz",
            created_by=self.user
        )

    def test_quiz_serializer(self):
        serializer = QuizSerializer(instance=self.quiz)

        self.assertEqual(
            serializer.data["title"],
            "Serializer Quiz"
        )

    def test_question_serializer_valid(self):
        serializer = QuestionSerializer(
            data={
                "quiz": self.quiz.id,
                "text": "What is Django framework?",
                "order": 1,
                "question_type": "single",
                "answer_options": [
                    {
                        "text": "Framework",
                        "is_correct": True
                    },
                    {
                        "text": "Database",
                        "is_correct": False
                    }
                ]
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_question_serializer_invalid(self):
        serializer = QuestionSerializer(
            data={
                "quiz": self.quiz.id,
                "text": "",
                "order": 1,
                "question_type": "single",
                "answer_options": []
            }
        )

        self.assertFalse(serializer.is_valid())