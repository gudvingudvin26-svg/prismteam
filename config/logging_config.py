import logging
import logging.config
import logging.handlers
from pathlib import Path
from django.conf import settings

LOG_DIR = Path(settings.BASE_DIR) / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = '[%(asctime)s] %(levelname)s %(name)s (%(filename)s:%(lineno)d): %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
            'datefmt': DATE_FORMAT,
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': DATE_FORMAT,
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'app.log',
            'formatter': 'verbose',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'error.log',
            'formatter': 'verbose',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 3,
        },
        'ws_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'websocket.log',
            'formatter': 'verbose',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'django_console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'app': {
            'handlers': ['app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ws': {
            'handlers': ['ws_file', 'app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'django_console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'app_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'channels': {
            'handlers': ['app_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['app_file', 'console'],
        'level': 'INFO',
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'app.{name}')
