"""Модуль валидации данных квизов: варианты ответов, целостность квиза, уникальность."""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def validate_answer_options_data(options_data, use_drf_exception=True, text_field='text', min_length=1, question_type=None):
    """
    Валидация списка вариантов ответа: тип, количество, уникальность, длина текста.

    Args:
        options_data: Список/кортеж словарей с вариантами ответов.
        use_drf_exception: Если True — выбрасывать DRF ValidationError, иначе Django.
        text_field: Имя поля с текстом варианта (по умолчанию 'text').
        min_length: Минимальная длина текста варианта (по умолчанию 1).

    Raises:
        ValidationError: При нарушении правил валидации.
    """
    ExceptionClass = DRFValidationError if use_drf_exception else DjangoValidationError
    if not isinstance(options_data, (list, tuple)):
        raise ExceptionClass("Данные вариантов ответов должны быть списком или кортежем.")
    if not options_data or len(options_data) < 2:
        raise ExceptionClass("Вопрос должен содержать минимум 2 варианта ответа.")
    answer_texts = set()
    for index, opt in enumerate(options_data):
        if not isinstance(opt, dict):
            raise ExceptionClass(f"Вариант ответа #{index + 1} должен быть словарём.")
        option_text = opt.get(text_field)
        if option_text is None:
            raise ExceptionClass(f"В варианте ответа #{index + 1} отсутствует поле '{text_field}'.")
        if not isinstance(option_text, str):
            raise ExceptionClass(f"Текст варианта ответа #{index + 1} должен быть строкой.")
        if len(option_text.strip()) < min_length:
            raise ExceptionClass(f"Текст варианта ответа #{index + 1} слишком короткий (минимум {min_length} символ).")
        normalized_text = option_text.strip().lower()
        if normalized_text in answer_texts:
            raise ExceptionClass(f"Вариант ответа #{index + 1} дублируется: '{option_text}'")
        answer_texts.add(normalized_text)


def validate_quiz_integrity(quiz, use_drf_exception=True):
    """
    Проверка целостности квиза: наличие вопросов, валидность текста, варианты ответов.

    Проверяет: квиз имеет вопросы, каждый вопрос имеет текст и ≥2 варианта,
    нет дубликатов ответов, корректное количество правильных ответов по типу вопроса.

    Args:
        quiz: Экземпляр модели Quiz для валидации.
        use_drf_exception: Если True — выбрасывать DRF ValidationError.

    Raises:
        ValidationError: При нарушении целостности данных квиза.
    """
    ExceptionClass = DRFValidationError if use_drf_exception else DjangoValidationError
    questions = quiz.questions.prefetch_related('answer_options').all()
    if not questions.exists():
        raise ExceptionClass("Квиз должен содержать хотя бы один вопрос.")
    for question in questions:
        if not question.text or not question.text.strip():
            raise ExceptionClass(f"Вопрос с ID {question.id} не имеет текста.")
        if len(question.text.strip()) < 5:
            raise ExceptionClass(f"Текст вопроса '{question.text[:20]}...' слишком короткий.")
        answers = question.answer_options.all()
        if len(answers) < 2:
            raise ExceptionClass(f"Вопрос '{question.text[:30]}' должен содержать минимум 2 варианта ответа.")
        answer_texts = set()
        for answer in answers:
            normalized = answer.text.strip().lower()
            if normalized in answer_texts:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' обнаружен дубликат ответа: '{answer.text}'")
            answer_texts.add(normalized)
        correct_count = sum(1 for a in answers if a.is_correct)
        if question.question_type == 'single':
            if correct_count != 1:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' для одиночного выбора должен быть ровно один правильный ответ (сейчас: {correct_count}).")
        elif question.question_type == 'multiple':
            if correct_count < 1:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' для множественного выбора должен быть хотя бы один правильный ответ (сейчас: {correct_count}).")
            if correct_count == len(answers):
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' нельзя отмечать ВСЕ варианты как правильные для множественного выбора.")


def validate_unique_answers_per_question(question):
    """
    Проверка уникальности текстов вариантов ответа в рамках одного вопроса.

    Args:
        question: Экземпляр модели Question для проверки.

    Raises:
        DjangoValidationError: При обнаружении дублирующихся ответов (без учёта регистра).
    """
    answers = question.answer_options.all()
    texts = [a.text.strip().lower() for a in answers]
    duplicates = [text for text in texts if texts.count(text) > 1]
    if duplicates:
        raise DjangoValidationError(f"В вопросе обнаружены дублирующиеся ответы: {set(duplicates)}")

def _is_meaningful_text(text):
    """
    Проверяет, содержит ли текст осмысленные символы.
    """
    if text is None:
        return False

    if not isinstance(text, str):
        return False

    return bool(text.strip())