from typing import Generic, Optional, TypeVar

from django.db import transaction
from django.db.models import Prefetch, QuerySet

from .models import Quiz, Question, AnswerOption
from .validators import validate_quiz_integrity

T = TypeVar('T')


class BaseRepository(Generic[T]):
    model = None

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls.model.objects.all()

    @classmethod
    def get_by_id(cls, obj_id: int) -> Optional[T]:
        return cls.get_queryset().filter(id=obj_id).first()

    @classmethod
    def create(cls, **kwargs) -> T:
        return cls.model.objects.create(**kwargs)

    @classmethod
    def update(cls, instance: T, **kwargs) -> T:
        for field, value in kwargs.items():
            setattr(instance, field, value)

        instance.save()

        return instance

    @classmethod
    def delete(cls, instance: T) -> None:
        instance.delete()

    @classmethod
    def filter(cls, **kwargs) -> QuerySet:
        return cls.get_queryset().filter(**kwargs)


class QuizRepository(BaseRepository[Quiz]):
    model = Quiz

    @classmethod
    def get_queryset(cls):
        return (
            cls.model.objects
            .select_related('created_by')
            .prefetch_related(
                Prefetch(
                    'questions',
                    queryset=Question.objects.prefetch_related(
                        'answer_options'
                    ).order_by('order')
                )
            )
        )

    @classmethod
    def get_user_quizzes(cls, user) -> QuerySet[Quiz]:
        return (
            cls.get_queryset()
            .filter(created_by=user)
            .order_by('-id')
        )

    @classmethod
    def get_user_quiz_by_id(cls, user, quiz_id: int) -> Optional[Quiz]:
        return (
            cls.get_queryset()
            .filter(created_by=user, id=quiz_id)
            .first()
        )

    @classmethod
    @transaction.atomic
    def publish_quiz(cls, quiz: Quiz) -> Quiz:
        validate_quiz_integrity(
            quiz,
            use_drf_exception=True
        )

        quiz.save()

        return quiz


class QuestionRepository(BaseRepository[Question]):
    model = Question

    @classmethod
    def get_queryset(cls):
        return (
            cls.model.objects
            .select_related('quiz')
            .prefetch_related('answer_options')
        )

    @classmethod
    def get_quiz_questions(cls, quiz_id: int) -> QuerySet[Question]:
        return (
            cls.get_queryset()
            .filter(quiz_id=quiz_id)
            .order_by('order')
        )

    @classmethod
    def get_user_question(cls, user, question_id: int) -> Optional[Question]:
        return (
            cls.get_queryset()
            .filter(
                id=question_id,
                quiz__created_by=user
            )
            .first()
        )

    @classmethod
    @transaction.atomic
    def create_question_with_answers(
        cls,
        answer_options: list,
        **question_data
    ) -> Question:
        question = cls.model.objects.create(**question_data)

        AnswerOption.objects.bulk_create([
            AnswerOption(
                question=question,
                **option
            )
            for option in answer_options
        ])

        return question

    @classmethod
    @transaction.atomic
    def update_question_with_answers(
        cls,
        instance: Question,
        answer_options: Optional[list] = None,
        **question_data
    ) -> Question:

        for field, value in question_data.items():
            setattr(instance, field, value)

        instance.save()

        if answer_options is not None:
            instance.answer_options.all().delete()

            AnswerOption.objects.bulk_create([
                AnswerOption(
                    question=instance,
                    **option
                )
                for option in answer_options
            ])

        return instance


class AnswerOptionRepository(BaseRepository[AnswerOption]):
    model = AnswerOption

    @classmethod
    def get_queryset(cls):
        return (
            cls.model.objects
            .select_related('question', 'question__quiz')
        )

    @classmethod
    def get_question_answers(cls, question_id: int):
        return cls.get_queryset().filter(question_id=question_id)