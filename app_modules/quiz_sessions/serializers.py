from rest_framework import serializers
from .models import QuizSession
from app_modules.quiz.models import Quiz

class QuizSessionSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField(write_only=True, required=False)
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), required=False)

    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'quiz_id', 'code', 'participant_name', 'status', 'created_at', 'started_at', 'ended_at']
        read_only_fields = ['code', 'created_at']

    def validate(self, attrs):
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