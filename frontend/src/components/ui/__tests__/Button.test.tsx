import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../index'

describe('Button Component', () => {
  test('рендерит кнопку с текстом', () => {
    render(<Button>Нажми меня</Button>)
    expect(screen.getByText('Нажми меня')).toBeInTheDocument()
  })

  test('вызывает onClick при клике', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Кликни</Button>)

    fireEvent.click(screen.getByText('Кликни'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('отображает состояние загрузки', () => {
    render(<Button isLoading>Загружается</Button>)
    expect(screen.getByText('Загрузка...')).toBeInTheDocument()
  })

  test('кнопка неактивна при isLoading', () => {
    render(<Button isLoading>Загружается</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  test('применяет правильные классы для primary варианта', () => {
    render(<Button variant="primary">Primary</Button>)
    const button = screen.getByRole('button')
    expect(button.className).toContain('bg-blue-600')
  })

  test('применяет правильные классы для danger варианта', () => {
    render(<Button variant="danger">Danger</Button>)
    const button = screen.getByRole('button')
    expect(button.className).toContain('bg-red-600')
  })

  test('применяет правильные размеры для sm', () => {
    render(<Button size="sm">Маленькая</Button>)
    const button = screen.getByRole('button')
    expect(button.className).toContain('px-3 py-1.5 text-sm')
  })

  test('применяет fullWidth класс', () => {
    render(<Button fullWidth>На всю ширину</Button>)
    const button = screen.getByRole('button')
    expect(button.className).toContain('w-full')
  })

  test('кнопка неактивна при disabled', () => {
    render(<Button disabled>Неактивная</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})