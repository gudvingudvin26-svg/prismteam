"""Утилиты логирования приложения: форматтеры и фабрики логгеров.

Предоставляет два форматтера для вывода логов:
• JsonFormatter — структурированный JSON-формат для агрегаторов (ELK, Sentry, CloudWatch).
• PlainTextFormatter — человекочитаемый текст для отладки и консоли разработки.

Также включает фабричные функции для получения именованных логгеров:
'login_log', 'quiz_log', 'ws' — с централизованной конфигурацией.
"""
import logging
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Форматтер для вывода логов в структурированном JSON-формате.

    Предназначен для интеграции с системами централизованного сбора логов.
    Каждый лог-запись содержит метаданные: временная метка, уровень, имя логгера,
    сообщение, исходный модуль/функция/строка. Поддерживает добавление
    контекстных полей (user_id, quiz_id, session_id) через extra={} при логировании.
    При наличии исключения (exc_info) автоматически добавляет traceback в поле 'exception'.

    Пример вывода:
    {
        "timestamp": "2024-06-01T12:34:56.789012",
        "level": "ERROR",
        "name": "quiz_log",
        "message": "Ошибка валидации квиза",
        "module": "validators",
        "function": "validate_quiz_integrity",
        "line": 42,
        "user_id": 123,
        "quiz_id": 456,
        "exception": "Traceback (most recent call last):\\n..."
    }
    """

    def __init__(self):
        """Инициализация форматтера: вызов базового конструктора logging.Formatter."""
        super().__init__()

    def format(self, record):
        """Форматирование записи лога в JSON-строку с метаданными и контекстом.

        Последовательность действий:
        1. Создаёт базовый словарь с обязательными полями (timestamp, level, message и др.).
        2. Добавляет контекстные поля (user_id, quiz_id, session_id), если они переданы через extra={}.
        3. При наличии исключения (record.exc_info) форматирует traceback и добавляет в 'exception'.
        4. Сериализует словарь в JSON-строку с поддержкой кириллицы (ensure_ascii=False).

        Args:
            record: Экземпляр logging.LogRecord с данными события.

        Returns:
            str: JSON-строка с отформатированной лог-записью.
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'quiz_id'):
            log_entry['quiz_id'] = record.quiz_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id

        if hasattr(record, 'exc_info') and record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class PlainTextFormatter(logging.Formatter):
    """Форматтер для вывода логов в человекочитаемом текстовом формате.

    Предназначен для отладки в консоли разработки и локального тестирования.
    Формат строки:
    [YYYY-MM-DD HH:MM:SS] LEVEL logger_name (filename.py:line): сообщение

    Пример:
    [2024-06-01 12:34:56] ERROR quiz_log (validators.py:42): Ошибка валидации квиза
    """

    def __init__(self):
        """Инициализация форматтера с заданным шаблоном и форматом даты.

        Шаблон включает: временную метку, уровень, имя логгера,
        имя файла, номер строки и сообщение. Дата форматируется
        как 'год-месяц-день часы:минуты:секунды'.
        """
        super().__init__(
            fmt='[%(asctime)s] %(levelname)s %(name)s (%(filename)s:%(lineno)d): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def get_login_logger():
    """Возвращает именованный логгер для событий аутентификации.

    Предназначен для логирования входа, выхода, регистрации и ошибок
    авторизации. Используется в представлениях и сервисах, связанных
    с управлением сессиями пользователей.

    Returns:
        logging.Logger: Экземпляр логгера с именем 'login_log'.
    """
    return logging.getLogger('login_log')


def get_quiz_logger():
    """Возвращает именованный логгер для событий работы с квизами.

    Предназначен для логирования создания, обновления, удаления квизов,
    валидации, публикации и ошибок бизнес-логики. Используется в
    ViewSet'ах, валидаторах и фабриках квизов.

    Returns:
        logging.Logger: Экземпляр логгера с именем 'quiz_log'.
    """
    return logging.getLogger('quiz_log')


def get_ws_logger():
    """Возвращает именованный логгер для событий WebSocket-соединений.

    Предназначен для логирования подключения/отключения клиентов,
    обработки сообщений, ошибок вещания и таймаутов. Используется
    в consumers.py и утилитах реального времени.

    Returns:
        logging.Logger: Экземпляр логгера с именем 'ws'.
    """
    return logging.getLogger('ws')