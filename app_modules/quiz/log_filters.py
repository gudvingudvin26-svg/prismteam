import logging

class InfoOrErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO or record.levelno == logging.ERROR or record.levelno == logging.CRITICAL