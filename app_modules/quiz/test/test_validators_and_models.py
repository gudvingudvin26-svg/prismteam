import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from app_modules.quiz.models import (
    AnswerOption,
    Question,
    Quiz,
    User,
    generate_token,
)
from app_modules.quiz.validators import (
    validate_answer_options_data,
    validate_quiz_integrity,
)


class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="organizer",
            email=f"organizer_{uuid.uuid4()}@test.com",
            password="testpass"
        )

        cls.quiz = Quiz.objects.create(
            title="Django Quiz",
            created_by=cls.user
        )

        cls.question = Question.objects.create(
            quiz=cls.quiz,
            text="What is Python programming language?",
            order=1,
            question_type="single"
        )

        cls.ans1 = AnswerOption.objects.create(
            question=cls.question,
            text="Programming language",
            is_correct=True
        )

        cls.ans2 = AnswerOption.objects.create(
            question=cls.question,
            text="Snake species",
            is_correct=False
        )

    def test_generate_token_length_and_uniqueness(self):
        token = generate_token()

        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 16)
        self.assertNotEqual(token, generate_token())

    def test_quiz_str(self):
        self.assertEqual(str(self.quiz), "Django Quiz")

    def test_question_str_truncation(self):
        long_text = "A" * 100

        q = Question.objects.create(
            quiz=self.quiz,
            text=long_text,
            order=2,
            question_type="single"
        )

        self.assertIn("A" * 50, str(q))
        self.assertEqual(
            len(str(q)),
            len(f"{self.quiz.title} - ") + 50
        )

    def test_question_str_short(self):
        self.assertEqual(
            str(self.question),
            f"{self.quiz.title} - What is Python programming language?"
        )

    def test_answer_option_str(self):
        self.assertEqual(
            str(self.ans1),
            "[✓] Programming language"
        )

        self.assertEqual(
            str(self.ans2),
            "[✗] Snake species"
        )

    def test_question_clean_valid(self):
        self.question.full_clean()

    def test_question_clean_whitespace_only(self):
        q = Question(
            quiz=self.quiz,
            text="   ",
            order=3,
            question_type="single"
        )

        # Валидация текста сейчас выполняется в validators.py / serializers
        try:
            q.full_clean()
        except DjangoValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly")


class TestValidators(TestCase):
    def setUp(self):
        self.valid_options = [
            {
                "text": "Correct answer option",
                "is_correct": True
            },
            {
                "text": "Incorrect answer option",
                "is_correct": False
            },
        ]

        self.user = User.objects.create_user(
            username="u",
            email=f"u_{uuid.uuid4()}@test.com",
            password="p"
        )

        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            created_by=self.user
        )

        # Первый вопрос
        self.q1 = Question.objects.create(
            quiz=self.quiz,
            text="What is the capital of France?",
            order=1,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=self.q1,
            text="Paris",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=self.q1,
            text="London",
            is_correct=False
        )

        # Второй вопрос — нужен для прохождения validate_quiz_integrity
        self.q2 = Question.objects.create(
            quiz=self.quiz,
            text="Which planet is known as the Red Planet?",
            order=2,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=self.q2,
            text="Mars",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=self.q2,
            text="Venus",
            is_correct=False
        )

    def test_valid_options(self):
        try:
            validate_answer_options_data(self.valid_options)
        except Exception as e:
            self.fail(f"validate_answer_options_data raised exception: {e}")

    def test_less_than_two_options(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [self.valid_options[0]],
                use_drf_exception=False
            )

    def test_not_a_list(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                "not a list",
                use_drf_exception=False
            )

    def test_non_dict_option(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [self.valid_options[0], "string"],
                use_drf_exception=False
            )

    def test_missing_text_field(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"is_correct": True},
                    self.valid_options[1]
                ],
                use_drf_exception=False
            )

    def test_non_string_text(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"text": 123, "is_correct": True},
                    self.valid_options[1]
                ],
                use_drf_exception=False
            )

    def test_whitespace_only_text(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"text": "   ", "is_correct": True},
                    self.valid_options[1]
                ],
                use_drf_exception=False
            )

    def test_drf_exception_mode(self):
        with self.assertRaises(DRFValidationError):
            validate_answer_options_data(
                [],
                use_drf_exception=True
            )

    def test_valid_quiz_integrity(self):
        try:
            validate_quiz_integrity(self.quiz)
        except Exception as e:
            self.fail(f"validate_quiz_integrity raised exception: {e}")

    def test_quiz_without_questions(self):
        empty_quiz = Quiz.objects.create(
            title="Empty",
            created_by=self.user
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                empty_quiz,
                use_drf_exception=False
            )

    def test_question_with_empty_text(self):
        invalid_quiz = Quiz.objects.create(
            title="Invalid Quiz",
            created_by=self.user
        )

        q1 = Question.objects.create(
            quiz=invalid_quiz,
            text="",
            order=1,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q1,
            text="Answer A",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q1,
            text="Answer B",
            is_correct=False
        )

        q2 = Question.objects.create(
            quiz=invalid_quiz,
            text="Second valid question text",
            order=2,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q2,
            text="Option 1",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q2,
            text="Option 2",
            is_correct=False
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                invalid_quiz,
                use_drf_exception=False
            )

    def test_question_with_short_text(self):
        invalid_quiz = Quiz.objects.create(
            title="Short Text Quiz",
            created_by=self.user
        )

        q1 = Question.objects.create(
            quiz=invalid_quiz,
            text="Hi",
            order=1,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q1,
            text="Option A",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q1,
            text="Option B",
            is_correct=False
        )

        q2 = Question.objects.create(
            quiz=invalid_quiz,
            text="Another fully valid question text",
            order=2,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q2,
            text="Correct answer",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q2,
            text="Wrong answer",
            is_correct=False
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                invalid_quiz,
                use_drf_exception=False
            )

    def test_question_with_less_than_two_answers(self):
        invalid_quiz = Quiz.objects.create(
            title="Few Answers Quiz",
            created_by=self.user
        )

        q1 = Question.objects.create(
            quiz=invalid_quiz,
            text="Valid question with one answer?",
            order=1,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q1,
            text="Only one answer",
            is_correct=True
        )

        q2 = Question.objects.create(
            quiz=invalid_quiz,
            text="Second valid question for integrity",
            order=2,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q2,
            text="Correct",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q2,
            text="Incorrect",
            is_correct=False
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                invalid_quiz,
                use_drf_exception=False
            )

    def test_question_with_zero_correct_answers(self):
        invalid_quiz = Quiz.objects.create(
            title="Zero Correct Quiz",
            created_by=self.user
        )

        q1 = Question.objects.create(
            quiz=invalid_quiz,
            text="Question without correct answer?",
            order=1,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q1,
            text="Wrong 1",
            is_correct=False
        )

        AnswerOption.objects.create(
            question=q1,
            text="Wrong 2",
            is_correct=False
        )

        q2 = Question.objects.create(
            quiz=invalid_quiz,
            text="Another valid question text",
            order=2,
            question_type="single"
        )

        AnswerOption.objects.create(
            question=q2,
            text="Right",
            is_correct=True
        )

        AnswerOption.objects.create(
            question=q2,
            text="Wrong",
            is_correct=False
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                invalid_quiz,
                use_drf_exception=False
            )