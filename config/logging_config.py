"""Конфигурация логирования Django-приложения: файлы, консоль, ротация, иерархия логгеров."""
import logging
import logging.config
import logging.handlers
from pathlib import Path

# Директория для файлов логов (создаётся при отсутствии)
LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Форматы вывода: подробный для файлов, упрощённый для консоли
LOG_FORMAT = '[%(asctime)s] %(levelname)s %(name)s (%(filename)s:%(lineno)d): %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Словарь конфигурации logging.dictConfig: форматы, фильтры, хэндлеры, логгеры
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': LOG_FORMAT, 'datefmt': DATE_FORMAT},
        'simple': {'format': '%(asctime)s %(levelname)s %(message)s', 'datefmt': DATE_FORMAT},
    },
    'filters': {
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'handlers': {
        'app_file': {  # Основной лог: DEBUG+, ротация 10МБ, 5 бэкапов
            'level': 'DEBUG', 'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'app.log', 'formatter': 'verbose',
            'maxBytes': 10 * 1024 * 1024, 'backupCount': 5,
        },
        'error_file': {  # Только ошибки: ротация 10МБ, 3 бэкапа
            'level': 'ERROR', 'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'error.log', 'formatter': 'verbose',
            'maxBytes': 10 * 1024 * 1024, 'backupCount': 3,
        },
        'ws_file': {  # Логи WebSocket: ротация 5МБ, 3 бэкапа
            'level': 'DEBUG', 'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'websocket.log', 'formatter': 'verbose',
            'maxBytes': 5 * 1024 * 1024, 'backupCount': 3,
        },
        'console': {  # Консоль для разработки: все уровни, простой формат
            'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple',
        },
        'django_console': {  # Консоль для Django: только WARNING+ при DEBUG=True
            'level': 'WARNING', 'class': 'logging.StreamHandler', 'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'app': {'handlers': ['app_file', 'console'], 'level': 'DEBUG', 'propagate': False},
        'ws': {'handlers': ['ws_file', 'app_file', 'console'], 'level': 'DEBUG', 'propagate': False},
        'django': {'handlers': ['console', 'django_console'], 'level': 'INFO', 'propagate': True},
        'django.request': {'handlers': ['error_file', 'app_file'], 'level': 'ERROR', 'propagate': False},
        'channels': {'handlers': ['app_file', 'console'], 'level': 'INFO', 'propagate': False},
    },
    'root': {'handlers': ['app_file', 'console'], 'level': 'INFO'},
}


def setup_logging():
    """Применение конфигурации логирования через logging.config.dictConfig."""
    logging.config.dictConfig(LOGGING)


def get_logger(name: str) -> logging.Logger:
    """Получение логгера с префиксом 'app.' для единообразия имён в проекте.

    Args:
        name (str): Имя подлоггера (например, 'auth', 'quiz', 'ws').

    Returns:
        logging.Logger: Настроенный экземпляр логгера.
    """
    return logging.getLogger(f'app.{name}')