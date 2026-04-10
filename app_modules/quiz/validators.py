"""Валидаторы для проверки целостности викторин, вопросов и вариантов ответов."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def validate_answer_options_data(options_data, use_drf_exception=True, text_field='text', min_length=1):
    """
    Проверяет локальную корректность данных вариантов ответов для вопроса.

    Ожидает список словарей с ключами:
        - text_field (по умолчанию 'text'): текст варианта ответа
        - 'is_correct': булево значение, указывающее правильный ли вариант
    """
    ExceptionClass = DRFValidationError if use_drf_exception else DjangoValidationError

    # 1. Базовая проверка структуры данных
    if not isinstance(options_data, (list, tuple)):
        raise ExceptionClass("Данные вариантов ответов должны быть списком или кортежем.")

    if not options_data or len(options_data) < 2:
        raise ExceptionClass("Вопрос должен содержать минимум 2 варианта ответа.")

    correct_count = 0

    # 2. Поэлементная валидация каждого варианта
    for index, opt in enumerate(options_data):
        if not isinstance(opt, dict):
            raise ExceptionClass(f"Вариант ответа #{index + 1} должен быть словарём.")

        # Проверка наличия и валидности текста
        option_text = opt.get(text_field)

        if option_text is None:
            raise ExceptionClass(f"В варианте ответа #{index + 1} отсутствует поле '{text_field}'.")

        if not isinstance(option_text, str):
            raise ExceptionClass(f"Текст варианта ответа #{index + 1} должен быть строкой.")

        if len(option_text.strip()) < min_length:
            raise ExceptionClass(f"Текст варианта ответа #{index + 1} слишком короткий (минимум {min_length} символ).")

        # Подсчёт правильных ответов
        if opt.get('is_correct') is True:  # строгая проверка на True
            correct_count += 1

    # 3. Финальная проверка: ровно один правильный ответ
    if correct_count != 1:
        raise ExceptionClass(f"Среди вариантов ответа должен быть ровно один правильный. Найдено: {correct_count}.")


def validate_quiz_integrity(quiz, use_drf_exception=True):
    """
    Проверяет целостность уже сохраненной викторины в базе данных.

    Выполняет проверки на наличие вопросов, корректность их текста,
    минимальное количество вариантов ответов и наличие ровно одного правильного ответа.
    Оптимизировано через `prefetch_related` для минимизации запросов к БД.
    """
    ExceptionClass = DRFValidationError if use_drf_exception else DjangoValidationError

    # Используем prefetch_related, чтобы избежать 100500 запросов к базе
    questions = quiz.questions.prefetch_related('answer_options').all()

    if not questions.exists():
        raise ExceptionClass("Квиз должен содержать хотя бы один вопрос.")

    for question in questions:
        if not question.text or not question.text.strip():
            raise ExceptionClass(f"Вопрос с ID {question.id} не имеет текста.")

        if len(question.text.strip()) < 5:
            raise ExceptionClass(f"Текст вопроса '{question.text[:20]}...' слишком короткий.")

        # Проверка ответов
        answers = question.answer_options.all()
        if len(answers) < 2:
            raise ExceptionClass(f"Вопрос '{question.text[:30]}' должен содержать минимум 2 варианта ответа.")

        correct_count = sum(1 for a in answers if a.is_correct)
        if correct_count != 1:
            raise ExceptionClass(
                f"В вопросе '{question.text[:30]}' должен быть ровно один правильный ответ (сейчас: {correct_count}).")