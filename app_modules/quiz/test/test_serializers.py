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
            password="testpass",
        )

        cls.quiz = Quiz.objects.create(
            title="Django Quiz",
            created_by=cls.user,
        )

        cls.question = Question.objects.create(
            quiz=cls.quiz,
            text="What is Python programming language?",
            order=1,
            question_type="single",
        )

        cls.ans1 = AnswerOption.objects.create(
            question=cls.question,
            text="Python is a programming language",
            is_correct=True,
        )

        cls.ans2 = AnswerOption.objects.create(
            question=cls.question,
            text="Python is a database",
            is_correct=False,
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
            question_type="single",
        )

        self.assertIn("A" * 50, str(q))
        self.assertEqual(
            len(str(q)),
            len(f"{self.quiz.title} - ") + 50,
        )

    def test_question_str_short(self):
        self.assertEqual(
            str(self.question),
            f"{self.quiz.title} - What is Python programming language?",
        )

    def test_answer_option_str(self):
        self.assertEqual(
            str(self.ans1),
            "[✓] Python is a programming language",
        )

        self.assertEqual(
            str(self.ans2),
            "[✗] Python is a database",
        )

    def test_question_clean_valid(self):
        self.question.full_clean()

    def test_question_clean_whitespace_only(self):
        q = Question(
            quiz=self.quiz,
            text="   ",
            order=3,
            question_type="single",
        )

        try:
            q.full_clean()
        except DjangoValidationError:
            self.fail(
                "full_clean() raised ValidationError unexpectedly"
            )


class TestValidators(TestCase):
    def setUp(self):
        self.valid_options = [
            {
                "text": "Correct answer option",
                "is_correct": True,
            },
            {
                "text": "Incorrect answer option",
                "is_correct": False,
            },
        ]

        self.user = User.objects.create_user(
            username="u",
            email=f"u_{uuid.uuid4()}@test.com",
            password="p",
        )

        self.quiz = Quiz.objects.create(
            title="Test",
            created_by=self.user,
        )

        self.q1 = Question.objects.create(
            quiz=self.quiz,
            text="First valid question text?",
            order=1,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=self.q1,
            text="Correct answer",
            is_correct=True,
        )

        AnswerOption.objects.create(
            question=self.q1,
            text="Incorrect answer",
            is_correct=False,
        )

        self.q2 = Question.objects.create(
            quiz=self.quiz,
            text="Second valid question text?",
            order=2,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=self.q2,
            text="Another correct answer",
            is_correct=True,
        )

        AnswerOption.objects.create(
            question=self.q2,
            text="Another incorrect answer",
            is_correct=False,
        )

    def test_valid_options(self):
        validate_answer_options_data(self.valid_options)

    def test_less_than_two_options(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [self.valid_options[0]],
                use_drf_exception=False,
            )

    def test_not_a_list(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                "not a list",
                use_drf_exception=False,
            )

    def test_non_dict_option(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [self.valid_options[0], "string"],
                use_drf_exception=False,
            )

    def test_missing_text_field(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"is_correct": True},
                    self.valid_options[1],
                ],
                use_drf_exception=False,
            )

    def test_non_string_text(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"text": 123, "is_correct": True},
                    self.valid_options[1],
                ],
                use_drf_exception=False,
            )

    def test_whitespace_only_text(self):
        with self.assertRaises(DjangoValidationError):
            validate_answer_options_data(
                [
                    {"text": "   ", "is_correct": True},
                    self.valid_options[1],
                ],
                use_drf_exception=False,
            )

    def test_drf_exception_mode(self):
        with self.assertRaises(DRFValidationError):
            validate_answer_options_data(
                [],
                use_drf_exception=True,
            )

    def test_valid_quiz_integrity(self):
        validate_quiz_integrity(self.quiz)

    def test_quiz_without_questions(self):
        empty_quiz = Quiz.objects.create(
            title="Empty",
            created_by=self.user,
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                empty_quiz,
                use_drf_exception=False,
            )

    def test_question_with_empty_text(self):
        q = Question.objects.create(
            quiz=self.quiz,
            text="",
            order=3,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=q,
            text="Correct answer",
            is_correct=True,
        )

        AnswerOption.objects.create(
            question=q,
            text="Incorrect answer",
            is_correct=False,
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                self.quiz,
                use_drf_exception=False,
            )

    def test_question_with_short_text(self):
        q = Question.objects.create(
            quiz=self.quiz,
            text="Hi",
            order=4,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=q,
            text="Correct answer",
            is_correct=True,
        )

        AnswerOption.objects.create(
            question=q,
            text="Incorrect answer",
            is_correct=False,
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                self.quiz,
                use_drf_exception=False,
            )

    def test_question_with_less_than_two_answers(self):
        q = Question.objects.create(
            quiz=self.quiz,
            text="Valid question text?",
            order=5,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=q,
            text="Only answer option",
            is_correct=True,
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                self.quiz,
                use_drf_exception=False,
            )

    def test_question_with_zero_correct_answers(self):
        q = Question.objects.create(
            quiz=self.quiz,
            text="Valid question text?",
            order=6,
            question_type="single",
        )

        AnswerOption.objects.create(
            question=q,
            text="Wrong answer one",
            is_correct=False,
        )

        AnswerOption.objects.create(
            question=q,
            text="Wrong answer two",
            is_correct=False,
        )

        with self.assertRaises(DjangoValidationError):
            validate_quiz_integrity(
                self.quiz,
                use_drf_exception=False,
            )