# Quiz Service Documentation

Документация проекта генерируется через Sphinx с использованием `autodoc` и `napoleon`.

---

## Покрытые модули

| Модуль | Путь |
|---|---|
| Quiz models | `app_modules/quiz/models.py` |
| API views / serializers | `app_modules/quiz/views.py` |
| Repository layer | `app_modules/quiz/repositories.py` |
| WebSocket consumers | `app_modules/quiz/consumers.py` |
| Quiz sessions | `app_modules/quiz_sessions/` |

---

## Локальная сборка

### Требования

```bash
pip install sphinx sphinx-rtd-theme
```

### Сборка HTML

```bash
cd docs
make html
```

Результат сборки:

```text
build/html/index.html
```

### Очистка

```bash
make clean
```

---

## Добавление docstrings

Используется Google-style формат:

```python
def create_session(self, quiz_id: int):
    """Создание игровой сессии.

    Args:
        quiz_id: ID квиза.

    Returns:
        QuizSession: Созданная игровая сессия.
    """
```

После обновления docstrings пересобери документацию.
