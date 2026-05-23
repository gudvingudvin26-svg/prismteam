import { render, screen } from '@testing-library/react';
import { Card } from '../index';

describe('Card Component', () => {
  test('renders children', () => {
    render(
      <Card>
        <div>Контент карточки</div>
      </Card>
    );
    expect(screen.getByText('Контент карточки')).toBeInTheDocument();
  });

  test('applies base classes', () => {
    render(<Card>Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('bg-white rounded-lg shadow-md');
  });

  test('applies padding sm', () => {
    render(<Card padding="sm">Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('p-3');
  });

  test('applies padding md by default', () => {
    render(<Card>Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('p-5');
  });

  test('applies padding lg', () => {
    render(<Card padding="lg">Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('p-8');
  });

  test('applies padding none', () => {
    render(<Card padding="none">Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('p-0');
  });

  test('applies additional className', () => {
    render(<Card className="custom-class">Контент</Card>);
    const card = screen.getByText('Контент').parentElement;
    expect(card?.className).toContain('custom-class');
  });

  test('renders complex children', () => {
    render(
      <Card>
        <h2>Заголовок</h2>
        <p>Параграф</p>
        <button>Кнопка</button>
      </Card>
    );
    expect(screen.getByText('Заголовок')).toBeInTheDocument();
    expect(screen.getByText('Параграф')).toBeInTheDocument();
    expect(screen.getByText('Кнопка')).toBeInTheDocument();
  });
});