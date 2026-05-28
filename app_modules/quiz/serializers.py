import logging

from rest_framework import serializers

from .models import User, Question, AnswerOption, Quiz
from .validators import (
    validate_answer_options_data,
    _is_meaningful_text,
)
quiz_log = logging.getLogger('quiz_log')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnswerOptionSerializer(serializers.Serializer):
    text = serializers.CharField(
        min_length=1,
        max_length=255,
        trim_whitespace=True
    )
    is_correct = serializers.BooleanField(default=False)

    def validate_text(self, value):
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Текст ответа должен быть осмысленным.'
            )

        return value

class QuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, required=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'quiz',
            'text',
            'order',
            'question_type',
            'timer',
            'points',
            'answer_options'
        ]

    def validate_text(self, value):
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Текст вопроса должен быть осмысленным.'
            )

        return value

    def validate_timer(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Таймер должен быть больше 0.'
            )

        return value

    def validate(self, data):
        instance = getattr(self, 'instance', None)

        options = data.get('answer_options')

        question_type = data.get(
            'question_type',
            instance.question_type if instance else None
        )

        if options is not None:
            validate_answer_options_data(
                options,
                use_drf_exception=True,
                question_type=question_type
            )

        return data

    def create(self, validated_data):
        options_data = validated_data.pop('answer_options')

        question = Question.objects.create(**validated_data)

        AnswerOption.objects.bulk_create([
            AnswerOption(question=question, **opt)
            for opt in options_data
        ])

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('answer_options', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if options_data is not None:
            instance.answer_options.all().delete()

            AnswerOption.objects.bulk_create([
                AnswerOption(question=instance, **opt)
                for opt in options_data
            ])

        quiz_log.info(
            'Organizer updated question in the quiz successfully'
        )
        return instance


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_by',
            'access_token',
            'timer',
            'points_per_question',
            'questions'
        ]

        read_only_fields = ['access_token']

    def validate_title(self, value):
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Название квиза должно быть осмысленным.'
            )

        return value

    def validate_timer(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Таймер квиза должен быть больше 0.'
            )

        return value
