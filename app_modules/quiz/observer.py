import logging

observer_log = logging.getLogger('observer')

class GameObserver:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type: str, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        observer_log.info(f"Подписчик добавлен на событие '{event_type}'")

    def unsubscribe(self, event_type: str, callback):
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def notify(self, event_type: str, **data):
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(**data)
            except Exception as e:
                observer_log.error(f"Ошибка в обработчике события '{event_type}': {e}")

game_observer = GameObserver()