import React from 'react'
import { render, screen } from '@testing-library/react'
import { Card } from '../index'

describe('Card Component', () => {
  test('рендерит дочерние элементы', () => {
    render(
      <Card>
        <div>Контент карточки</div>
      </Card>
    )
    expect(screen.getByText('Контент карточки')).toBeInTheDocument()
  })

  test('применяет базовые классы', () => {
    render(<Card>Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('bg-white rounded-lg shadow-md')
  })

  test('применяет padding sm', () => {
    render(<Card padding="sm">Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('p-3')
  })

  test('применяет padding md по умолчанию', () => {
    render(<Card>Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('p-5')
  })

  test('применяет padding lg', () => {
    render(<Card padding="lg">Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('p-8')
  })

  test('применяет padding none', () => {
    render(<Card padding="none">Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('p-0')
  })

  test('применяет дополнительный className', () => {
    render(<Card className="custom-class">Контент</Card>)
    const card = screen.getByText('Контент').parentElement
    expect(card?.className).toContain('custom-class')
  })

  test('рендерит сложные дочерние элементы', () => {
    render(
      <Card>
        <h2>Заголовок</h2>
        <p>Параграф</p>
        <button>Кнопка</button>
      </Card>
    )
    expect(screen.getByText('Заголовок')).toBeInTheDocument()
    expect(screen.getByText('Параграф')).toBeInTheDocument()
    expect(screen.getByText('Кнопка')).toBeInTheDocument()
  })
})