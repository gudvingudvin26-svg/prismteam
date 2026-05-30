"""Модуль наблюдения за событиями игры: реализация паттерна Observer для подписки и уведомлений."""
import logging

observer_log = logging.getLogger('observer')


class GameObserver:
    """Реализация паттерна Observer: управление подписчиками и рассылка событий."""

    def __init__(self):
        """Инициализация: создание пустого словаря подписчиков по типам событий."""
        self._subscribers = {}

    def subscribe(self, event_type: str, callback):
        """Подписка колбэка на событие: добавление в список обработчиков типа event_type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        observer_log.info(f"Подписчик добавлен на событие '{event_type}'")

    def unsubscribe(self, event_type: str, callback):
        """Отписка колбэка от события: удаление из списка обработчиков типа event_type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def notify(self, event_type: str, **data):
        """Уведомление всех подписчиков события: вызов колбэков с передачей данных."""
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(**data)
            except Exception as e:
                observer_log.error(f"Ошибка в обработчике события '{event_type}': {e}")


# Глобальный экземпляр наблюдателя для использования в приложении
game_observer = GameObserver()