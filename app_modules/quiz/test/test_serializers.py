import uuid
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from app_modules.quiz.models import User, Quiz, Question, AnswerOption
from app_modules.quiz.serializers import QuizSerializer, QuestionSerializer, AnswerOptionSerializer


class TestSerializers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="org",
            email=f"org_{uuid.uuid4()}@test.com",
            password="pass"
        )
        cls.quiz = Quiz.objects.create(title="Test Quiz", created_by=cls.user)
        cls.question = Question.objects.create(quiz=cls.quiz, text="Capital of France?", order=1)
        cls.opt1 = AnswerOption.objects.create(question=cls.question, text="Paris", is_correct=True)
        cls.opt2 = AnswerOption.objects.create(question=cls.question, text="London", is_correct=False)

    def test_answer_option_valid(self):
        data = {"text": "Option A", "is_correct": False}
        s = AnswerOptionSerializer(data=data)
        self.assertTrue(s.is_valid())

    def test_answer_option_missing_text(self):
        s = AnswerOptionSerializer(data={"is_correct": True})
        self.assertFalse(s.is_valid())
        self.assertIn("text", s.errors)

    def test_answer_option_too_short_text(self):
        s = AnswerOptionSerializer(data={"text": "", "is_correct": False})
        self.assertFalse(s.is_valid())

    def test_question_create_valid(self):
        data = {
            "quiz": self.quiz.id,
            "text": "2 + 2 = ?",
            "order": 2,
            "answer_options": [
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False},
            ]
        }
        s = QuestionSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        question = s.save()
        self.assertEqual(question.answer_options.count(), 2)

    def test_question_create_missing_options(self):
        data = {"quiz": self.quiz.id, "text": "No options", "order": 2, "answer_options": []}
        s = QuestionSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_question_create_no_correct_answer(self):
        data = {
            "quiz": self.quiz.id, "text": "Test?", "order": 3,
            "answer_options": [{"text": "A", "is_correct": False}, {"text": "B", "is_correct": False}]
        }
        s = QuestionSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_question_update_replaces_options(self):
        data = {
            "quiz": self.quiz.id, "text": "Updated?", "order": 1,
            "answer_options": [
                {"text": "Yes", "is_correct": True},
                {"text": "No", "is_correct": False}
            ]
        }
        s = QuestionSerializer(self.question, data=data, partial=True)
        self.assertTrue(s.is_valid(), s.errors)
        updated_q = s.save()
        self.assertEqual(updated_q.answer_options.count(), 2)
        self.assertEqual(updated_q.text, "Updated?")

    def test_question_validate_empty_text(self):
        data = {"quiz": self.quiz.id, "text": "   ", "answer_options": [
            {"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}
        ]}
        s = QuestionSerializer(data=data)
        self.assertFalse(s.is_valid())
        error_str = str(s.errors)
        self.assertTrue(
            "Текст вопроса не может быть пустым" in error_str or
            "may not be blank" in error_str
        )

    def test_quiz_create_sets_created_by(self):
        class MockRequest:
            user = self.user

        context = {"request": MockRequest()}
        data = {"title": "New Quiz", "description": "Desc"}
        s = QuizSerializer(data=data, context=context)
        self.assertTrue(s.is_valid(), s.errors)
        quiz = s.save()
        self.assertEqual(quiz.created_by, self.user)
        self.assertIsNotNone(quiz.access_token)

    def test_quiz_serializer_questions_readonly(self):
        s = QuizSerializer(self.quiz)
        self.assertIn("questions", s.data)
        self.assertIsInstance(s.data["questions"], list)
        self.assertEqual(len(s.data["questions"]), 1)

    def test_quiz_serializer_created_by_hidden(self):
        class MockRequest:
            user = self.user

        context = {"request": MockRequest()}
        data = {"title": "Test", "created_by": 999}
        s = QuizSerializer(data=data, context=context)
        self.assertTrue(s.is_valid())
        quiz = s.save()
        self.assertEqual(quiz.created_by, self.user)