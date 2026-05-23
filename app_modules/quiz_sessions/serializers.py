from rest_framework import serializers
from .models import QuizSession

class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'code', 'participant_name', 'status', 'created_at', 'started_at', 'ended_at']
        read_only_fields = ['code', 'created_at']