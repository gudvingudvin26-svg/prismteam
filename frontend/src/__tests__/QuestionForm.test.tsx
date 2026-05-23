import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
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

  test('renders question form', () => {
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

  test('calls onDelete when delete button clicked', () => {
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

  test('updates question text on change', () => {
    render(
      <QuestionForm
        question={mockQuestion}
        index={0}
        onChange={mockOnChange}
        onDelete={mockOnDelete}
      />
    );

    const textInput = screen.getByLabelText('Текст вопроса');
    fireEvent.change(textInput, { target: { value: 'New question' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockQuestion,
      text: 'New question'
    });
  });

  test('adds new answer option', () => {
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

  test('shows error when question text is empty on blur', () => {
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