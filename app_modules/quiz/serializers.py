import logging
from rest_framework import serializers
from .models import User, Question, AnswerOption, Quiz
from .validators import validate_answer_options_data

quiz_log = logging.getLogger('quiz_log')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnswerOptionSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=1, max_length=255, trim_whitespace=True)
    is_correct = serializers.BooleanField(default=False)


class QuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, required=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'order', 'question_type', 'timer', 'points', 'answer_options']

    def validate_answer_options(self, value):
        validate_answer_options_data(value)
        return value

    def validate(self, data):
        text = data.get('text')
        if text is not None and not text.strip():
            raise serializers.ValidationError("Текст вопроса не может быть пустым.")

        options = data.get('answer_options')
        if options is not None:
            validate_answer_options_data(options, use_drf_exception=True)

        question_type = data.get('question_type')
        if question_type:
            if question_type == 'single':
                correct_count = sum(1 for opt in options if opt.get('is_correct'))
                if correct_count != 1:
                    raise serializers.ValidationError(
                        {"answer_options": "Для одиночного выбора должен быть ровно один правильный ответ"})
            elif question_type == 'multiple':
                correct_count = sum(1 for opt in options if opt.get('is_correct'))
                if correct_count < 1:
                    raise serializers.ValidationError(
                        {"answer_options": "Для множественного выбора должен быть хотя бы один правильный ответ"})

        return data

    def create(self, validated_data):
        options_data = validated_data.pop('answer_options')
        question = Question.objects.create(**validated_data)

        AnswerOption.objects.bulk_create([
            AnswerOption(question=question, **opt) for opt in options_data
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
                AnswerOption(question=instance, **opt) for opt in options_data
            ])

        quiz_log.info(f'Organizer updated question in the quiz successfully')
        return instance


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_by', 'access_token', 'timer', 'points_per_question',
                  'questions']
        read_only_fields = ['access_token']