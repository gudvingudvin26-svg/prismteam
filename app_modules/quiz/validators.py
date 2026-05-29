# validators.py

import re
from collections import Counter
from typing import Any, Iterable, Sequence

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

MIN_QUESTION_TEXT_LENGTH = 5
MIN_ANSWER_TEXT_LENGTH = 1

MIN_OPTIONS_COUNT = 2
MIN_OPTIONS_COUNT_MULTIPLE = 3

MAX_REPEATED_CHAR_RATIO = 0.7

LETTER_PATTERN = re.compile(r"[A-Za-zА-Яа-яЁё]")


def _get_exception_class(use_drf_exception: bool):
    """
    Возвращает нужный класс исключения в зависимости от контекста использования.
    """
    return DRFValidationError if use_drf_exception else DjangoValidationError


def _is_meaningful_text(text: str) -> bool:
    """
    Лёгкая эвристическая проверка текста на осмысленность.

    Проверяет:
    - наличие хотя бы одной буквы (латиница/кириллица);
    - текст не должен состоять только из цифр/символов/пробелов;
    - не более 70% одинаковых символов.

    Примеры НЕвалидных строк:
    - "111111"
    - "??????"
    - "аааааааа"
    - "     "
    - "@@@@1234"

    Примеры валидных строк:
    - "Столица Франции"
    - "Python 3"
    - "2 + 2 = 4?"
    """
    if not isinstance(text, str):
        return False

    normalized = text.strip()

    if not normalized:
        return False

    if not LETTER_PATTERN.search(normalized):
        return False

    compact_text = re.sub(r"\s+", "", normalized)

    if not compact_text:
        return False

    char_counts = Counter(compact_text)
    most_common_count = char_counts.most_common(1)[0][1]
    repeated_ratio = most_common_count / len(compact_text)

    if repeated_ratio > MAX_REPEATED_CHAR_RATIO:
        return False

    return True


def validate_answer_options_data(
    options_data: Sequence[dict[str, Any]],
    *,
    use_drf_exception: bool = True,
    text_field: str = 'text',
    min_length: int = MIN_ANSWER_TEXT_LENGTH,
    question_type: str | None = None,
) -> None:
    """
    Валидирует данные вариантов ответов.

    Проверяет:
    - тип данных;
    - минимальное количество вариантов;
    - структуру каждого варианта;
    - валидность текста;
    - правила для single/multiple вопросов.

    :param options_data: список вариантов ответа
    :param use_drf_exception: использовать DRF ValidationError
    :param text_field: название текстового поля
    :param min_length: минимальная длина текста
    :param question_type: тип вопроса (single/multiple)
    """
    ExceptionClass = _get_exception_class(use_drf_exception)

    if not isinstance(options_data, (list, tuple)):
        raise ExceptionClass("Данные вариантов ответов должны быть списком или кортежем.")

    required_options_count = (
        MIN_OPTIONS_COUNT_MULTIPLE
        if question_type == 'multiple'
        else MIN_OPTIONS_COUNT
    )

    if len(options_data) < required_options_count:
        if question_type == 'multiple':
            raise ExceptionClass(
                f"Вопрос с множественным выбором должен содержать минимум "
                f"{MIN_OPTIONS_COUNT_MULTIPLE} варианта ответа."
            )

    answer_texts = set()
    for index, opt in enumerate(options_data):
        raise ExceptionClass(
            f"Вопрос должен содержать минимум {MIN_OPTIONS_COUNT} варианта ответа."
        )

    for index, opt in enumerate(options_data, start=1):
        if not isinstance(opt, dict):
            raise ExceptionClass(f"Вариант ответа #{index} должен быть словарём.")

        option_text = opt.get(text_field)

        if option_text is None:
            raise ExceptionClass(
                f"В варианте ответа #{index} отсутствует поле '{text_field}'."
            )

        if not isinstance(option_text, str):
            raise ExceptionClass(
                f"Текст варианта ответа #{index} должен быть строкой."
            )

        normalized_text = option_text.strip()

        if len(normalized_text) < min_length:
            raise ExceptionClass(
                f"Текст варианта ответа #{index} слишком короткий "
                f"(минимум {min_length} символ)."
            )

        if not _is_meaningful_text(normalized_text):
            raise ExceptionClass(
                f"Текст варианта ответа #{index} содержит бессмысленный или некорректный текст."
            )

    if question_type:
        correct_count = sum(
            1 for opt in options_data
            if opt.get('is_correct')
        )

        if question_type == 'single' and correct_count != 1:
            raise ExceptionClass(
                "Для одиночного выбора должен быть ровно один правильный ответ."
            )
        normalized_text = option_text.strip().lower()
        if normalized_text in answer_texts:
            raise ExceptionClass(f"Вариант ответа #{index + 1} дублируется: '{option_text}'")
        answer_texts.add(normalized_text)


        if question_type == 'multiple' and correct_count < 2:
            raise ExceptionClass(
                "Для множественного выбора должно быть минимум 2 правильных ответа."
            )


def validate_quiz_integrity(
    quiz,
    *,
    use_drf_exception: bool = True,
) -> None:
    """
    Полная проверка целостности квиза перед публикацией.

    Проверяет:
    - наличие таймера;
    - наличие вопросов;
    - корректность текста вопросов;
    - количество вариантов ответа;
    - корректность правильных ответов;
    - валидность текстов вариантов ответа.
    """
    ExceptionClass = _get_exception_class(use_drf_exception)

    if quiz.timer is not None and quiz.timer <= 0:
        raise ExceptionClass(
            "Квиз должен иметь корректный лимит времени (значение должно быть больше 0)."
        )

    # ==========================================
    # Оптимизированная загрузка
    # ==========================================
    questions = list(
        quiz.questions.prefetch_related('answer_options')
    )

    if len(questions) < 2:
        raise ExceptionClass("Квиз должен содержать минимум 2 вопроса.")

    for question in questions:
        question_text = (question.text or "").strip()

        if not question_text:
            raise ExceptionClass(
                f"Вопрос с ID {question.id} не имеет текста."
            )

        if len(question_text) < MIN_QUESTION_TEXT_LENGTH:
            raise ExceptionClass(
                f"Текст вопроса '{question_text[:20]}...' слишком короткий."
            )

        if not _is_meaningful_text(question_text):
            raise ExceptionClass(
                f"Текст вопроса '{question_text[:30]}' содержит бессмысленный или некорректный текст."
            )

        answer_texts = set()
        for answer in answers:
            normalized = answer.text.strip().lower()
            if normalized in answer_texts:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' обнаружен дубликат ответа: '{answer.text}'")
            answer_texts.add(normalized)

        correct_count = sum(1 for a in answers if a.is_correct)
        answers = list(question.answer_options.all())

        required_options_count = (
            MIN_OPTIONS_COUNT_MULTIPLE
            if question.question_type == 'multiple'
            else MIN_OPTIONS_COUNT
        )

        if len(answers) < required_options_count:
            if question.question_type == 'multiple':
                raise ExceptionClass(
                    f"Вопрос '{question_text[:30]}' должен содержать минимум "
                    f"{MIN_OPTIONS_COUNT_MULTIPLE} варианта ответа."
                )

            raise ExceptionClass(
                f"Вопрос '{question_text[:30]}' должен содержать минимум "
                f"{MIN_OPTIONS_COUNT} варианта ответа."
            )

        correct_count = 0

        for answer_index, answer in enumerate(answers, start=1):
            answer_text = (answer.text or "").strip()

            if not answer_text:
                raise ExceptionClass(
                    f"В вопросе '{question_text[:30]}' найден пустой вариант ответа."
                )

            if not _is_meaningful_text(answer_text):
                raise ExceptionClass(
                    f"Вариант ответа #{answer_index} "
                    f"в вопросе '{question_text[:30]}' содержит бессмысленный текст."
                )

            if answer.is_correct:
                correct_count += 1

        if question.question_type == 'single':
            if correct_count != 1:
                raise ExceptionClass(
                    f"В вопросе '{question.text[:30]}' для одиночного выбора должен быть ровно один правильный ответ (сейчас: {correct_count}).")
                raise ExceptionClass(
                    f"В вопросе '{question_text[:30]}' "
                    f"для одиночного выбора должен быть ровно один "
                    f"правильный ответ (сейчас: {correct_count})."
                )


        elif question.question_type == 'multiple':
            if correct_count < 1:
                raise ExceptionClass(
                    f"В вопросе '{question.text[:30]}' для множественного выбора должен быть хотя бы один правильный ответ (сейчас: {correct_count}).")
            if correct_count == len(answers):
                raise ExceptionClass(
                    f"В вопросе '{question.text[:30]}' нельзя отмечать ВСЕ варианты как правильные для множественного выбора.")


def validate_unique_answers_per_question(question):
    answers = question.answer_options.all()
    texts = [a.text.strip().lower() for a in answers]
    duplicates = [text for text in texts if texts.count(text) > 1]
    if duplicates:
        raise DjangoValidationError(f"В вопросе обнаружены дублирующиеся ответы: {set(duplicates)}")
            if correct_count < 2:
                raise ExceptionClass(
                    f"В вопросе '{question_text[:30]}' "
                    f"для множественного выбора должно быть минимум "
                    f"2 правильных ответа (сейчас: {correct_count})."

                )