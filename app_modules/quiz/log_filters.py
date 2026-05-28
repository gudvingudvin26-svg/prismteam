import logging

class InfoOrErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO or record.levelno == logging.ERROR or record.levelno == logging.CRITICAL


class UserContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = 'anonymous'
        if not hasattr(record, 'quiz_id'):
            record.quiz_id = 'none'
        if not hasattr(record, 'session_id'):
            record.session_id = 'none'
        return True