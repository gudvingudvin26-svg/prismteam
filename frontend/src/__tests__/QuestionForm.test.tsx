   import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QuestionForm from '../components/quiz/QuestionForm';

describe('QuestionForm', () => {
  const mockQuestion = {
    id: '1',
    text: '',
    order: 1,
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  };

  const mockOnChange = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('рендерит форму вопроса', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );
    expect(screen.getByText('Вопрос 1')).toBeInTheDocument();
  });

  test('вызывает onDelete при нажатии на кнопку удаления', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );
    const deleteButton = screen.getByText('Удалить');
    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledTimes(1);
  });

  test('обновляет текст вопроса при изменении', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );

    const textInput = screen.getByLabelText('Текст вопроса');
    fireEvent.change(textInput, { target: { value: 'Новый вопрос' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockQuestion,
      text: 'Новый вопрос'
    });
  });

  test('добавляет новый вариант ответа', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );

    const addButton = screen.getByText('+ Добавить вариант');
    fireEvent.click(addButton);

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockQuestion,
      options: [...mockQuestion.options, { text: '', is_correct: false }]
    });
  });

  test('показывает ошибку при пустом тексте вопроса после потери фокуса', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );

    const textInput = screen.getByLabelText('Текст вопроса');
    fireEvent.blur(textInput);

    expect(screen.getByText('Текст вопроса обязателен')).toBeInTheDocument();
  });
});