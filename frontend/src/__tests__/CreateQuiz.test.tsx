import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateQuiz from '../components/quiz/CreateQuiz';

jest.mock('../api/quizzes', () => ({
  quizzesApi: {
    createQuiz: jest.fn().mockResolvedValue({ data: { id: 1 } }),
    createQuestion: jest.fn().mockResolvedValue({})
  }
}));

describe('CreateQuiz', () => {
  test('renders create quiz form', () => {
    render(<CreateQuiz />);
    expect(screen.getByText('Создание нового квиза')).toBeInTheDocument();
  });

  test('shows error when title is empty on submit', () => {
    render(<CreateQuiz />);
    const submitButton = screen.getByText('Сохранить квиз');
    fireEvent.click(submitButton);
    expect(screen.getByText('Введите название квиза')).toBeInTheDocument();
  });

  test('shows error when less than 2 questions', () => {
    render(<CreateQuiz />);
    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Test Quiz' } });

    const submitButton = screen.getByText('Сохранить квиз');
    fireEvent.click(submitButton);

    expect(screen.getByText('Добавьте хотя бы два вопроса')).toBeInTheDocument();
  });

  test('adds new question when clicking add question button', () => {
    render(<CreateQuiz />);
    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);
    fireEvent.click(addButton);
    expect(screen.getAllByText(/Вопрос \d+/).length).toBe(2);
  });

  test('validation passes with valid data', () => {
    render(<CreateQuiz />);

    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Valid Quiz' } });

    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);
    fireEvent.click(addButton);

    const questionInputs = screen.getAllByLabelText('Текст вопроса');
    fireEvent.change(questionInputs[0], { target: { value: 'First question?' } });
    fireEvent.change(questionInputs[1], { target: { value: 'Second question?' } });

    const optionInputs = screen.getAllByPlaceholderText(/Вариант 1/);
    fireEvent.change(optionInputs[0], { target: { value: 'Answer 1' } });
    fireEvent.change(optionInputs[2], { target: { value: 'Answer 1 for Q2' } });

    const radios = screen.getAllByRole('radio');
    fireEvent.click(radios[0]);
    fireEvent.click(radios[2]);

    const submitButton = screen.getByText('Сохранить квиз');
    fireEvent.click(submitButton);

    expect(screen.queryByText('Введите название квиза')).not.toBeInTheDocument();
    expect(screen.queryByText('Добавьте хотя бы два вопроса')).not.toBeInTheDocument();
  });
});