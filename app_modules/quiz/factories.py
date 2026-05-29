from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from .models import Quiz, Question, AnswerOption
import logging

logger = logging.getLogger('quiz_log')

class QuizFactory:
    @staticmethod
    def create_quiz(data: Dict[str, Any], user) -> Quiz:
        quiz = Quiz.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            created_by=user,
            timer=data.get('timer'),
            points_per_question=data.get('points_per_question', 100)
        )
        logger.info(f"Quiz created: {quiz.id} by user {user.username}")
        return quiz