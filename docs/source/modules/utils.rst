Utilities, Validation and Logging
=================================

validators.py
-------------

Содержит проверки:

* корректности структуры квиза;
* уникальности вариантов ответов;
* корректности данных вопросов.

logging_config.py
-----------------

* ``JsonFormatter`` — JSON-формат логов;
* ``PlainTextFormatter`` — текстовый вывод логов;
* функции получения логгеров.

log_filters.py
--------------

* ``InfoOrErrorFilter`` — фильтрация логов;
* ``UserContextFilter`` — добавление контекста пользователя.

consumers.py
------------

**QuizConsumer**
    WebSocket-консьюмер для многопользовательских квизов.