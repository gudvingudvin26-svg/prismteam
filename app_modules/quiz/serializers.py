"""Сериализаторы для викторин, вопросов и вариантов ответов."""

from rest_framework import serializers

from .models import AnswerOption, Question, Quiz
from .validators import validate_answer_options_data

from rest_framework import serializers
from .models import Question, AnswerOption


class AnswerOptionSerializer(serializers.Serializer):
    """Вложенный сериализатор только для записи/валидации вариантов ответа."""
    text = serializers.CharField(min_length=1, max_length=255, trim_whitespace=True)
    is_correct = serializers.BooleanField(default=False)


class QuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, required=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'order', 'answer_options']

    def validate_answer_options(self, value):
        """
        Вызывается DRF автоматически для поля answer_options.
        value здесь уже десериализован в список словарей.
        """
        validate_answer_options_data(value)
        return value

    def validate(self, data):
        text = data.get('text')
        if text is not None and not text.strip():
            raise serializers.ValidationError("Текст вопроса не может быть пустым.")

        options = data.get('answer_options')
        if options is not None:
            validate_answer_options_data(options, use_drf_exception=True)

        return data

    def create(self, validated_data):
        options_data = validated_data.pop('answer_options')
        question = Question.objects.create(**validated_data)

        # bulk_create в 5-10 раз быстрее цикла с .create()
        AnswerOption.objects.bulk_create([
            AnswerOption(question=question, **opt) for opt in options_data
        ])
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('answer_options', None)

        # Обновляем основные поля вопроса
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            instance.answer_options.all().delete()
            AnswerOption.objects.bulk_create([
                AnswerOption(question=instance, **opt) for opt in options_data
            ])
        return instance

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
        """Метаданные сериализатора викторины."""
        model = Quiz
        fields = ['id', 'title', 'description', 'created_by', 'access_token', 'questions']
        # access_token генерируется автоматически, его не нужно передавать
        read_only_fields = ['access_token']