from .models import Quiz


class QuizFactory:

    @staticmethod
    def create_quiz(data: dict, user) -> Quiz:
        """
        Создаёт квиз от имени пользователя.
        data – провалидированный словарь с полями (title, description, timer и т.д.).
        user – экземпляр пользователя-создателя.
        """
        data.pop('created_by', None)
        quiz = Quiz.objects.create(created_by=user, **data)
        return quiz