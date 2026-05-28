import logging
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):

    def __init__(self):
        super().__init__()

    def format(self, record):
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

    def __init__(self):
        super().__init__(
            fmt='[%(asctime)s] %(levelname)s %(name)s (%(filename)s:%(lineno)d): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def get_login_logger():
    return logging.getLogger('login_log')


def get_quiz_logger():
    return logging.getLogger('quiz_log')


def get_ws_logger():
    return logging.getLogger('ws')