import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../index';

describe('Input Component', () => {
  test('renders input element', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  test('displays label when provided', () => {
    render(<Input label="Имя пользователя" />);
    expect(screen.getByText('Имя пользователя')).toBeInTheDocument();
  });

  test('displays error message', () => {
    render(<Input error="Обязательное поле" />);
    expect(screen.getByText('Обязательное поле')).toBeInTheDocument();
  });

  test('applies error styles when error', () => {
    render(<Input error="Ошибка" />);
    const input = screen.getByRole('textbox');
    expect(input.className).toContain('border-red-500');
  });

  test('applies fullWidth class', () => {
    render(<Input fullWidth />);
    const input = screen.getByRole('textbox');
    expect(input.className).toContain('w-full');
  });

  test('passes value and onChange', () => {
    const handleChange = jest.fn();
    render(<Input value="тест" onChange={handleChange} />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveValue('тест');

    fireEvent.change(input, { target: { value: 'новый текст' } });
    expect(handleChange).toHaveBeenCalled();
  });

  test('input is disabled when disabled', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  test('input has type text by default', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'text');
  });

  test('input can have different type', () => {
    render(<Input type="password" />);
    expect(screen.getByLabelText('input')).toHaveAttribute('type', 'password');
  });
});