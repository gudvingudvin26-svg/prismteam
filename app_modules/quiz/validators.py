from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def validate_answer_options_data(options_data, use_drf_exception=True, text_field='text', min_length=1):
    ExceptionClass = DRFValidationError if use_drf_exception else DjangoValidationError

    if not isinstance(options_data, (list, tuple)):
        raise ExceptionClass("Данные вариантов ответов должны быть списком или кортежем.")

    if not options_data or len(options_data) < 2:
        raise ExceptionClass("Вопрос должен содержать минимум 2 варианта ответа.")

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


def validate_quiz_integrity(quiz, use_drf_exception=True):
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

        correct_count = sum(1 for a in answers if a.is_correct)

        if question.question_type == 'single':
            if correct_count != 1:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' для одиночного выбора должен быть ровно один правильный ответ (сейчас: {correct_count}).")
        elif question.question_type == 'multiple':
            if correct_count < 1:
                raise ExceptionClass(f"В вопросе '{question.text[:30]}' для множественного выбора должен быть хотя бы один правильный ответ (сейчас: {correct_count}).")