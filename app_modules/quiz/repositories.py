"""Репозитории для доступа к данным: базовый CRUD и специализированные запросы."""
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Prefetch
from typing import TypeVar, Generic, Optional

T = TypeVar('T')  # Тип-параметр для обобщённой типизации репозиториев


class BaseRepository(Generic[T]):
    """Базовый репозиторий с типовыми CRUD-операциями для любой модели."""
    model: type[T] | None = None

    def __init__(self):
        """Инициализация: проверка наличия указанной модели."""
        if self.model is None:
            raise ValueError("Необходимо указать модель в атрибуте model")

    def get_all(self) -> QuerySet[T]:
        """Возврат всех записей модели как QuerySet."""
        return self.model.objects.all()

    def get_by_id(self, obj_id) -> Optional[T]:
        """Получение объекта по первичному ключу или None при отсутствии."""
        try:
            return self.model.objects.get(pk=obj_id)
        except ObjectDoesNotExist:
            return None

    def create(self, **kwargs) -> T:
        """Создание новой записи модели с переданными параметрами."""
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        """Обновление полей экземпляра модели и сохранение."""
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """Удаление экземпляра модели из базы данных."""
        instance.delete()

    def filter(self, **kwargs) -> QuerySet[T]:
        """Фильтрация записей модели по произвольным условиям."""
        return self.model.objects.filter(**kwargs)


class QuizRepository(BaseRepository):
    """Специализированный репозиторий для модели Quiz с расширенными запросами."""

    def get_with_questions(self, quiz_id: int, user):
        """
        Получение квиза с предзагруженными вопросами и вариантами ответов.

        Фильтрует по ID квиза и пользователю-создателю, оптимизирует запрос
        через prefetch_related для связанных данных.

        Args:
            quiz_id: ID искомого квиза.
            user: Пользователь, которому должен принадлежать квиз.

        Returns:
            Quiz или None, если не найден или нет прав доступа.
        """
        return self.model.objects.filter(
            id=quiz_id, created_by=user
        ).prefetch_related('questions__answer_options').first()