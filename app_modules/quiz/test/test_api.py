from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework import serializers as drf_serializers
from django.contrib.auth.models import User

from app_modules.quiz.models import Quiz, Question, AnswerOption
from app_modules.quiz.serializers import AnswerOptionSerializer  # Ваш текущий сериализатор


class QuizAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="org1", password="pass1")
        cls.user2 = User.objects.create_user(username="org2", password="pass2")
        cls.client1 = APIClient()
        cls.client2 = APIClient()
        cls.client1.force_authenticate(user=cls.user1)
        cls.client2.force_authenticate(user=cls.user2)

        cls.quiz1 = Quiz.objects.create(title="Quiz1", created_by=cls.user1)
        cls.q1 = Question.objects.create(quiz=cls.quiz1, text="What is Django?", order=1)
        AnswerOption.objects.create(question=cls.q1, text="Web Framework", is_correct=True)
        AnswerOption.objects.create(question=cls.q1, text="Database", is_correct=False)

    def test_list_quiz_only_own(self):
        Quiz.objects.create(title="Quiz2", created_by=self.user2)
        res1 = self.client1.get(reverse("quiz-list"))
        res2 = self.client2.get(reverse("quiz-list"))
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res1.data), 1)
        self.assertEqual(len(res2.data), 1)

    def test_create_quiz(self):
        res = self.client1.post(reverse("quiz-list"), {"title": "New", "description": "Desc"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.filter(title="New").count(), 1)
        self.assertEqual(Quiz.objects.get(title="New").created_by, self.user1)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(reverse("quiz-list"))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_publish_valid_quiz(self):
        res = self.client1.post(reverse("quiz-publish", kwargs={"pk": self.quiz1.pk}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("готов к публикации", res.data["status"])

    def test_publish_invalid_quiz(self):
        empty_quiz = Quiz.objects.create(title="Empty", created_by=self.user1)
        res = self.client1.post(reverse("quiz-publish", kwargs={"pk": empty_quiz.pk}))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("хотя бы один вопрос", res.data["detail"])

    def test_delete_own_quiz(self):
        res = self.client1.delete(reverse("quiz-detail", kwargs={"pk": self.quiz1.pk}))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=self.quiz1.pk).exists())


class QuestionAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org1 = User.objects.create_user(username="org1", password="p")
        cls.org2 = User.objects.create_user(username="org2", password="p")
        cls.client1 = APIClient()
        cls.client1.force_authenticate(user=cls.org1)

        cls.quiz1 = Quiz.objects.create(title="Q1", created_by=cls.org1)
        cls.quiz2 = Quiz.objects.create(title="Q2", created_by=cls.org2)
        cls.question = Question.objects.create(quiz=cls.quiz1, text="First question?", order=1)
        AnswerOption.objects.create(question=cls.question, text="A", is_correct=True)
        AnswerOption.objects.create(question=cls.question, text="B", is_correct=False)

    def test_list_questions_isolation(self):
        Question.objects.create(quiz=self.quiz2, text="Other question", order=1)
        res = self.client1.get(reverse("question-list"))
        self.assertEqual(len(res.data), 1)

    def test_create_question_invalid_options(self):
        data = {
            "quiz": self.quiz1.id,
            "text": "New Question?",
            "order": 2,
            "answer_options": [{"text": "Only", "is_correct": True}]
        }
        res = self.client1.post(reverse("question-list"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_question(self):
        data = {
            "text": "Updated Question Text Here",
            "order": 1,
            "answer_options": [
                {"text": "Correct", "is_correct": True},
                {"text": "Wrong", "is_correct": False}
            ]
        }
        res = self.client1.patch(
            reverse("question-detail", kwargs={"pk": self.question.pk}),
            data,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Updated Question Text Here")
class _AnswerOptionModelSerializer(AnswerOptionSerializer):
    question = drf_serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = AnswerOption
        fields = ['id', 'question', 'text', 'is_correct']

    def create(self, validated_data):
        return AnswerOption.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AnswerOptionAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = User.objects.create_user(username="org", password="p")
        cls.quiz = Quiz.objects.create(title="Quiz", created_by=cls.org)
        cls.question = Question.objects.create(quiz=cls.quiz, text="Test question?", order=1)
        cls.option = AnswerOption.objects.create(question=cls.question, text="Opt", is_correct=True)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.org)
        # Подменяем сериализатор в ViewSet только для тестов
        from app_modules.quiz import views
        self.original_serializer = views.AnswerOptionViewSet.serializer_class
        views.AnswerOptionViewSet.serializer_class = _AnswerOptionModelSerializer

    def tearDown(self):
        from app_modules.quiz import views
        views.AnswerOptionViewSet.serializer_class = self.original_serializer

    def test_list_options(self):
        res = self.client.get(reverse("answerooption-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_option(self):
        data = {"question": self.question.id, "text": "NewOpt", "is_correct": False}
        res = self.client.post(reverse("answerooption-list"), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_option(self):
        res = self.client.delete(reverse("answerooption-detail", kwargs={"pk": self.option.pk}))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)