"""Сериализаторы для управления сессиями квизов: создание, валидация привязки, контроль полей."""
from rest_framework import serializers
from .models import QuizSession
from app_modules.quiz.models import Quiz

class QuizSessionSerializer(serializers.ModelSerializer):
    """Сериализатор сессии квиза: поддержка передачи квиза через ID или объект.

    Позволяет принимать quiz_id (write_only) для удобства клиентских запросов,
    автоматически разрешая его в ForeignKey quiz. Поля code и created_at
    защищены от перезаписи (read_only).
    """
    quiz_id = serializers.IntegerField(write_only=True, required=False)
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), required=False)

    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'quiz_id', 'code', 'participant_name', 'status', 'created_at', 'started_at', 'ended_at']
        read_only_fields = ['code', 'created_at']

    def validate(self, attrs):
        """Валидация и нормализация связи с квизом: преобразование quiz_id в объект.

        Проверяет наличие quiz_id или quiz. Если передан только quiz_id,
        загружает соответствующий объект Quiz и подставляет его в attrs.
        При отсутствии обоих полей выбрасывает ошибку валидации.

        Args:
            attrs (dict): Входные данные сериализатора.

        Returns:
            dict: Нормализованные атрибуты с гарантированным полем 'quiz'.

        Raises:
            serializers.ValidationError: Если quiz_id не найден или оба поля отсутствуют.
        """
        quiz_id = attrs.get('quiz_id')
        quiz = attrs.get('quiz')

        if quiz_id and not quiz:
            try:
                attrs['quiz'] = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                raise serializers.ValidationError({"quiz": "Квиз с указанным quiz_id не найден."})

        if 'quiz' not in attrs:
            raise serializers.ValidationError({"quiz": "Это поле обязательно. Передайте 'quiz' или 'quiz_id'."})

        return attrs