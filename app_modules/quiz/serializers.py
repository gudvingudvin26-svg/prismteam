from rest_framework import serializers
from .models import Quiz, Question, AnswerOption

class AnswerOptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели варианта ответа (AnswerOption).

    Используется для представления отдельных вариантов ответов, связанных с вопросом.
    Включает идентификатор, ссылку на вопрос, текст ответа и флаг правильности.
    """

    class Meta:
        model = AnswerOption
        fields = ['id', 'question', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели вопроса (Question).

    Представляет вопрос викторины вместе со списком связанных вариантов ответов.

    Особенности:
    - Поле `answer_options` является вложенным списком объектов AnswerOptionSerializer.
    - Вложенные данные доступны только для чтения (read_only), так как создание/обновление
      вариантов ответов обычно обрабатывается отдельно или через nested writes (если реализовано).
    """
    # Вложенное отображение ответов (только для чтения)
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'order', 'answer_options']


class QuizSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели викторины (Quiz).

    Представляет основную информацию о викторине, включая вложенный список вопросов.

    Особенности:
    - Поле `questions` содержит вложенный список объектов QuestionSerializer (только для чтения).
    - Поле `created_by` автоматически заполняется текущим авторизованным пользователем при создании
      объекта и скрыто от входных данных пользователя.
    - Поле `access_token` генерируется автоматически на уровне модели/сигналов и доступно только
      для чтения в ответе API.
    """
    # Вложенное отображение вопросов (только для чтения)
    questions = QuestionSerializer(many=True, read_only=True)

    # Автоматически подставляем текущего пользователя в качестве создателя
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_by', 'access_token', 'questions']
        # access_token генерируется автоматически, его не нужно передавать
        read_only_fields = ['access_token']