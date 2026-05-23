import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateQuiz from '../components/quiz/CreateQuiz';

jest.mock('../services/api/quizzes', () => ({
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

  test('shows error when no questions added', () => {
    render(<CreateQuiz />);
    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Test Quiz' } });

    const submitButton = screen.getByText('Сохранить квиз');
    fireEvent.click(submitButton);

    expect(screen.getByText('Добавьте хотя бы один вопрос')).toBeInTheDocument();
  });

  test('adds new question when clicking add question button', () => {
    render(<CreateQuiz />);
    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);
    expect(screen.getByText('Вопрос 1')).toBeInTheDocument();
  });

  test('validation passes with valid data', () => {
    render(<CreateQuiz />);

    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Valid Quiz' } });

    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);

    const questionInput = screen.getByLabelText('Текст вопроса');
    fireEvent.change(questionInput, { target: { value: 'Test question?' } });

    const optionInput = screen.getByPlaceholderText('Вариант 1');
    fireEvent.change(optionInput, { target: { value: 'Answer 1' } });

    const radio = screen.getByRole('radio');
    fireEvent.click(radio);

    const submitButton = screen.getByText('Сохранить квиз');
    fireEvent.click(submitButton);

    expect(screen.queryByText('Введите название квиза')).not.toBeInTheDocument();
    expect(screen.queryByText('Добавьте хотя бы один вопрос')).not.toBeInTheDocument();
  });
});