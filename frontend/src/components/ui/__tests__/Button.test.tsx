import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../index';

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button>Нажми меня</Button>);
    expect(screen.getByText('Нажми меня')).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Кликни</Button>);

    fireEvent.click(screen.getByText('Кликни'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('displays loading state', () => {
    render(<Button isLoading>Загружается</Button>);
    expect(screen.getByText('Загрузка...')).toBeInTheDocument();
  });

  test('button is disabled when loading', () => {
    render(<Button isLoading>Загружается</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('applies correct classes for primary variant', () => {
    render(<Button variant="primary">Primary</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-blue-600');
  });

  test('applies correct classes for danger variant', () => {
    render(<Button variant="danger">Danger</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-red-600');
  });

  test('applies correct sizes for sm', () => {
    render(<Button size="sm">Маленькая</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('px-3 py-1.5 text-sm');
  });

  test('applies fullWidth class', () => {
    render(<Button fullWidth>На всю ширину</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('w-full');
  });

  test('button is disabled when disabled', () => {
    render(<Button disabled>Неактивная</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});