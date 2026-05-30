Services and Business Logic
===========================

factories.py
------------

**QuizFactory**
    Инкапсулирует создание квизов и бизнес-логику инициализации.

repositories.py
---------------

**BaseRepository**
    Базовый CRUD-репозиторий.

**QuizRepository**
    Репозиторий с расширенными запросами для квизов.

observer.py
-----------

**GameObserver**
    Реализация паттерна Observer для событий игры.

redis_utils.py
--------------

**RedisTimerManager**
    Управление таймерами вопросов через Redis.