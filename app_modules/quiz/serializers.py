import logging

from rest_framework import serializers

from .models import User, Question, AnswerOption, Quiz
from .repositories import QuestionRepository
from .validators import (
    validate_answer_options_data,
    _is_meaningful_text,
)

quiz_log = logging.getLogger('quiz_log')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя.

    Используется для:
    - создания пользователя;
    - отображения данных пользователя;
    - скрытия пароля из ответа API.

    Поля:
        id: Уникальный идентификатор пользователя.
        username: Имя пользователя.
        email: Электронная почта.
        phone: Номер телефона.
        password: Пароль пользователя (только запись).
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnswerOptionSerializer(serializers.Serializer):
    """
    Сериализатор варианта ответа.

    Используется внутри QuestionSerializer
    для обработки вариантов ответа вопроса.

    Поля:
        text: Текст варианта ответа.
        is_correct: Флаг правильного ответа.
    """

    text = serializers.CharField(
        min_length=1,
        max_length=255,
        trim_whitespace=True
    )

    is_correct = serializers.BooleanField(default=False)

    def validate_text(self, value):
        """
        Проверяет корректность текста ответа.

        Удаляет лишние пробелы и убеждается,
        что текст является осмысленным.

        Args:
            value (str): Текст ответа.

        Returns:
            str: Очищенный текст ответа.

        Raises:
            ValidationError: Если текст пустой
            или не содержит осмысленного содержимого.
        """
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Текст ответа должен быть осмысленным.'
            )

        return value


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопроса квиза.

    Поддерживает:
    - создание вопроса;
    - обновление вопроса;
    - вложенную работу с вариантами ответов;
    - валидацию параметров вопроса.

    Поля:
        id: Идентификатор вопроса.
        quiz: Связанный квиз.
        text: Текст вопроса.
        order: Порядок отображения.
        question_type: Тип вопроса.
        timer: Таймер вопроса.
        points: Количество баллов.
        answer_options: Список вариантов ответа.
    """

    answer_options = AnswerOptionSerializer(
        many=True,
        required=True
    )

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

        extra_kwargs = {
            'quiz': {'required': False}
        }

    def validate_text(self, value):
        """
        Проверяет текст вопроса.

        Args:
            value (str): Текст вопроса.

        Returns:
            str: Очищенный текст вопроса.

        Raises:
            ValidationError: Если текст не является осмысленным.
        """
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Текст вопроса должен быть осмысленным.'
            )

        return value

    def validate_timer(self, value):
        """
        Проверяет корректность таймера вопроса.

        Args:
            value (int | None): Значение таймера.

        Returns:
            int | None: Валидное значение таймера.

        Raises:
            ValidationError: Если таймер меньше либо равен нулю.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Таймер должен быть больше 0.'
            )

        return value

    def validate(self, data):
        """
        Выполняет общую валидацию вопроса.

        Проверяет корректность списка вариантов
        ответа в зависимости от типа вопроса.

        Args:
            data (dict): Данные сериализатора.

        Returns:
            dict: Провалидированные данные.
        """
        instance = getattr(self, 'instance', None)

        options = data.get('answer_options')

        question_type = (
            data.get('question_type')
            or getattr(instance, 'question_type', None)
        )

        if options is not None:
            validate_answer_options_data(
                options,
                use_drf_exception=True,
                question_type=question_type
            )

        return data

    def create(self, validated_data):
        """
        Создаёт вопрос вместе с вариантами ответов.

        Args:
            validated_data (dict): Провалидированные данные.

        Returns:
            Question: Созданный объект вопроса.
        """
        options_data = validated_data.pop('answer_options')

        question = Question.objects.create(**validated_data)

        AnswerOption.objects.bulk_create([
            AnswerOption(question=question, **option)
            for option in options_data
        ])

        return question

    def update(self, instance, validated_data):
        """
        Обновляет вопрос и связанные варианты ответов.

        Если список answer_options передан,
        старые варианты удаляются и создаются заново.

        Args:
            instance (Question): Обновляемый объект.
            validated_data (dict): Новые данные.

        Returns:
            Question: Обновлённый объект вопроса.
        """
        options_data = validated_data.pop(
            'answer_options',
            None
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if options_data is not None:
            instance.answer_options.all().delete()

            AnswerOption.objects.bulk_create([
                AnswerOption(
                    question=instance,
                    **option
                )
                for option in options_data
            ])

        quiz_log.info(
            'Organizer updated question in the quiz successfully'
        )

        return instance


class QuizSerializer(serializers.ModelSerializer):
    """
    Сериализатор квиза.

    Отвечает за:
    - создание квиза;
    - отображение списка вопросов;
    - автоматическую установку создателя квиза;
    - базовую валидацию данных.

    Поля:
        id: Идентификатор квиза.
        title: Название квиза.
        description: Описание квиза.
        created_by: Создатель квиза.
        access_token: Токен доступа.
        timer: Таймер квиза.
        points_per_question: Баллы за вопрос.
        questions: Список вопросов.
    """

    questions = QuestionSerializer(
        many=True,
        read_only=True
    )

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
        """
        Проверяет название квиза.

        Args:
            value (str): Название квиза.

        Returns:
            str: Очищенное название.

        Raises:
            ValidationError: Если название не является осмысленным.
        """
        value = value.strip()

        if not _is_meaningful_text(value):
            raise serializers.ValidationError(
                'Название квиза должно быть осмысленным.'
            )

        return value

    def validate_timer(self, value):
        """
        Проверяет корректность таймера квиза.

        Args:
            value (int | None): Таймер квиза.

        Returns:
            int | None: Валидное значение таймера.

        Raises:
            ValidationError: Если значение меньше либо равно нулю.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Таймер квиза должен быть больше 0.'
            )

        return value