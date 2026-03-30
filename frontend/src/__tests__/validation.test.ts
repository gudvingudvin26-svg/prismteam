   describe('Валидация форм', () => {
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

  test('валидация квиза: название обязательно', () => {
    const errors = validateQuiz('', 1);
    expect(errors.title).toBe('Название обязательно');
  });

  test('валидация квиза: хотя бы один вопрос обязателен', () => {
    const errors = validateQuiz('Тест', 0);
    expect(errors.questions).toBe('Добавьте хотя бы один вопрос');
  });

  test('валидация квиза: корректные данные проходят проверку', () => {
    const errors = validateQuiz('Тест', 1);
    expect(Object.keys(errors).length).toBe(0);
  });

  test('валидация вопроса: текст вопроса обязателен', () => {
    const errors = validateQuestion('', [{ text: 'Вариант 1', is_correct: true }]);
    expect(errors.text).toBe('Текст вопроса обязателен');
  });

  test('валидация вопроса: все варианты должны быть заполнены', () => {
    const errors = validateQuestion('Вопрос', [
      { text: 'Вариант 1', is_correct: true },
      { text: '', is_correct: false }
    ]);
    expect(errors.options).toBe('Все варианты должны быть заполнены');
  });

  test('валидация вопроса: должен быть выбран правильный ответ', () => {
    const errors = validateQuestion('Вопрос', [
      { text: 'Вариант 1', is_correct: false },
      { text: 'Вариант 2', is_correct: false }
    ]);
    expect(errors.options).toBe('Выберите правильный ответ');
  });

  test('валидация вопроса: корректные данные проходят проверку', () => {
    const errors = validateQuestion('Вопрос', [
      { text: 'Вариант 1', is_correct: true },
      { text: 'Вариант 2', is_correct: false }
    ]);
    expect(Object.keys(errors).length).toBe(0);
  });
});