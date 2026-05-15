import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CreateQuiz from '../components/quiz/CreateQuiz';

jest.mock('../services/api/quizzes', () => ({
  quizzesApi: {
    createQuiz: jest.fn().mockResolvedValue({ data: { id: 1 } }),
    createQuestion: jest.fn().mockResolvedValue({})
  }
}));

describe('CreateQuiz', () => {
  test('рендерит форму создания квиза', () => {
    render(<CreateQuiz />);
    expect(screen.getByText('Создание квиза')).toBeInTheDocument();
  });

  test('показывает ошибку при пустом названии', () => {
    render(<CreateQuiz />);
    const submitButton = screen.getByText('Создать квиз');
    fireEvent.click(submitButton);
    expect(screen.getByText('Название обязательно')).toBeInTheDocument();
  });

  test('показывает ошибку при отсутствии вопросов', () => {
    render(<CreateQuiz />);
    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Тестовый квиз' } });

    const submitButton = screen.getByText('Создать квиз');
    fireEvent.click(submitButton);

    expect(screen.getByText('Добавьте хотя бы один вопрос')).toBeInTheDocument();
  });

  test('добавляет новый вопрос при нажатии на кнопку', () => {
    render(<CreateQuiz />);
    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);
    expect(screen.getByText('Вопрос 1')).toBeInTheDocument();
  });

  test('валидация не срабатывает при корректных данных', () => {
    render(<CreateQuiz />);

    const titleInput = screen.getByLabelText('Название квиза');
    fireEvent.change(titleInput, { target: { value: 'Корректный квиз' } });

    const addButton = screen.getByText('+ Добавить вопрос');
    fireEvent.click(addButton);

    const questionInput = screen.getByLabelText('Текст вопроса');
    fireEvent.change(questionInput, { target: { value: 'Первый вопрос' } });

    const optionInput = screen.getByPlaceholderText('Вариант 1');
    fireEvent.change(optionInput, { target: { value: 'Ответ 1' } });

    const radio = screen.getByRole('radio');
    fireEvent.click(radio);

    const submitButton = screen.getByText('Создать квиз');
    fireEvent.click(submitButton);

    expect(screen.queryByText('Название обязательно')).not.toBeInTheDocument();
    expect(screen.queryByText('Добавьте хотя бы один вопрос')).not.toBeInTheDocument();
  });
});