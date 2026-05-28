from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Prefetch
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class BaseRepository(Generic[T]):
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


class QuizRepository(BaseRepository):
    def get_with_questions(self, quiz_id: int, user):
        return self.model.objects.filter(
            id=quiz_id, created_by=user
        ).prefetch_related('questions__answer_options').first()