import uuid

from django.test import TestCase

from app_modules.quiz.models import (
    User,
    Quiz,
    Question,
    AnswerOption,
)

from app_modules.quiz.repositories import (
    QuizRepository,
    QuestionRepository,
    AnswerOptionRepository,
)


class RepositoryTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="repo_user",
            email=f"repo_{uuid.uuid4()}@mail.com",
            password="pass123"
        )

        self.quiz = Quiz.objects.create(
            title="Repository Quiz",
            created_by=self.user
        )

    def test_quiz_repository_get_by_id(self):
        quiz = QuizRepository.get_by_id(self.quiz.id)

        self.assertEqual(quiz.title, "Repository Quiz")

    def test_quiz_repository_get_user_quizzes(self):
        quizzes = QuizRepository.get_user_quizzes(self.user)

        self.assertEqual(quizzes.count(), 1)

    def test_question_repository_create(self):
        question = QuestionRepository.create(
            quiz=self.quiz,
            text="Repository question?",
            order=1,
            question_type="single"
        )

        self.assertEqual(question.text, "Repository question?")

    def test_question_repository_get_quiz_questions(self):
        Question.objects.create(
            quiz=self.quiz,
            text="Question 1?",
            order=1
        )

        questions = QuestionRepository.get_quiz_questions(
            self.quiz.id
        )

        self.assertEqual(questions.count(), 1)

    def test_answer_option_repository(self):
        q = Question.objects.create(
            quiz=self.quiz,
            text="Question?",
            order=1
        )

        AnswerOption.objects.create(
            question=q,
            text="Answer",
            is_correct=True
        )

        answers = AnswerOptionRepository.get_question_answers(q.id)

        self.assertEqual(answers.count(), 1)