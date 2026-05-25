from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Prefetch
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Базовый репозиторий с общими CRUD-операциями."""
    model: type[T] | None = None

    def __init__(self):
        if self.model is None:
            raise ValueError("Необходимо указать модель в атрибуте model")

    def get_all(self) -> QuerySet[T]:
        return self.model.objects.all()

    def get_by_id(self, obj_id) -> Optional[T]:
        try:
            return self.model.objects.get(pk=obj_id)
        except ObjectDoesNotExist:
            return None

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    def filter(self, **kwargs) -> QuerySet[T]:
        return self.model.objects.filter(**kwargs)


class QuizRepository(BaseRepository['Quiz']):
    model = None  # Будет присвоено после инициализации

    def get_all_for_user(self, user) -> QuerySet['Quiz']:
        from .models import Question  # ленивый импорт для Prefetch
        return self.model.objects.filter(created_by=user).prefetch_related(
            Prefetch('questions', queryset=Question.objects.select_related('quiz').prefetch_related('answer_options'))
        ).select_related('created_by').order_by('-id')

    def publish(self, quiz):
        from .validators import validate_quiz_integrity
        validate_quiz_integrity(quiz, use_drf_exception=True)
        quiz.save()
        return quiz


class QuestionRepository(BaseRepository['Question']):
    model = None

    def get_all_for_user(self, user) -> QuerySet['Question']:
        return self.model.objects.filter(quiz__created_by=user).select_related('quiz').prefetch_related('answer_options')


class AnswerOptionRepository(BaseRepository['AnswerOption']):
    model = None

    def get_all_for_user(self, user) -> QuerySet['AnswerOption']:
        return self.model.objects.filter(question__quiz__created_by=user).select_related('question__quiz')


def _setup_repositories():
    """Присваиваем модели репозиториям после загрузки Django."""
    from .models import Quiz, Question, AnswerOption
    QuizRepository.model = Quiz
    QuestionRepository.model = Question
    AnswerOptionRepository.model = AnswerOption

_setup_repositories()