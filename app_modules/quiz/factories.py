from typing import Dict, Any

from .models import Quiz


class QuizFactory:
    """
    Фабрика для создания объектов Quiz.
    """

    @staticmethod
    def create_quiz(data: Dict[str, Any], user) -> Quiz:
        """
        Создание квиза от имени пользователя.

        :param data: провалидированные данные serializer.validated_data
        :param user: пользователь-создатель
        :return: объект Quiz
        """

        quiz_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'timer': data.get('timer'),
            'points_per_question': data.get('points_per_question', 100),
            'created_by': user,
        }

        quiz = Quiz.objects.create(**quiz_data)

        return quiz