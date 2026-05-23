import '@testing-library/jest-dom';

describe('Form Validation', () => {
  const validateQuiz = (title: string, questionsLength: number) => {
    const errors: { title?: string; questions?: string } = {};
    if (!title.trim()) errors.title = 'Название обязательно';
    if (questionsLength === 0) errors.questions = 'Добавьте хотя бы один вопрос';
    return errors;
  };

  const validateQuestion = (text: string, options: { text: string; is_correct: boolean }[]) => {
    const errors: { text?: string; options?: string } = {};
    if (!text.trim()) errors.text = 'Текст вопроса обязателен';
    if (options.some(opt => !opt.text.trim())) errors.options = 'Все варианты должны быть заполнены';
    if (!options.some(opt => opt.is_correct)) errors.options = 'Выберите правильный ответ';
    return errors;
  };

  test('quiz validation: title is required', () => {
    const errors = validateQuiz('', 1);
    expect(errors.title).toBe('Название обязательно');
  });

  test('quiz validation: at least one question is required', () => {
    const errors = validateQuiz('Test', 0);
    expect(errors.questions).toBe('Добавьте хотя бы один вопрос');
  });

  test('quiz validation: valid data passes', () => {
    const errors = validateQuiz('Test', 1);
    expect(Object.keys(errors).length).toBe(0);
  });

  test('question validation: text is required', () => {
    const errors = validateQuestion('', [{ text: 'Option 1', is_correct: true }]);
    expect(errors.text).toBe('Текст вопроса обязателен');
  });

  test('question validation: all options must be filled', () => {
    const errors = validateQuestion('Question', [
      { text: 'Option 1', is_correct: true },
      { text: '', is_correct: false }
    ]);
    expect(errors.options).toBe('Все варианты должны быть заполнены');
  });

  test('question validation: correct answer must be selected', () => {
    const errors = validateQuestion('Question', [
      { text: 'Option 1', is_correct: false },
      { text: 'Option 2', is_correct: false }
    ]);
    expect(errors.options).toBe('Выберите правильный ответ');
  });

  test('question validation: valid data passes', () => {
    const errors = validateQuestion('Question', [
      { text: 'Option 1', is_correct: true },
      { text: 'Option 2', is_correct: false }
    ]);
    expect(Object.keys(errors).length).toBe(0);
  });
});