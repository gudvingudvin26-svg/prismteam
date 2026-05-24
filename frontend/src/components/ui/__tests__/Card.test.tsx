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
    const { container } = render(<Card>Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('bg-white');
    expect(cardDiv.className).toContain('rounded-lg');
    expect(cardDiv.className).toContain('shadow-md');
  });

  test('applies padding sm', () => {
    const { container } = render(<Card padding="sm">Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('p-3');
  });

  test('applies padding md by default', () => {
    const { container } = render(<Card>Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('p-5');
  });

  test('applies padding lg', () => {
    const { container } = render(<Card padding="lg">Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('p-8');
  });

  test('applies padding none', () => {
    const { container } = render(<Card padding="none">Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('p-0');
  });

  test('applies additional className', () => {
    const { container } = render(<Card className="custom-class">Контент</Card>);
    const cardDiv = container.firstChild as HTMLElement;
    expect(cardDiv.className).toContain('custom-class');
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