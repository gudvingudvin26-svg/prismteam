import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from '../index'

describe('Input Component', () => {
  test('рендерит input элемент', () => {
    render(<Input />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  test('отображает label когда передан', () => {
    render(<Input label="Имя пользователя" />)
    expect(screen.getByText('Имя пользователя')).toBeInTheDocument()
  })

  test('отображает сообщение об ошибке', () => {
    render(<Input error="Обязательное поле" />)
    expect(screen.getByText('Обязательное поле')).toBeInTheDocument()
  })

  test('применяет стили ошибки при error', () => {
    render(<Input error="Ошибка" />)
    const input = screen.getByRole('textbox')
    expect(input.className).toContain('border-red-500')
  })

  test('применяет fullWidth класс', () => {
    render(<Input fullWidth />)
    const input = screen.getByRole('textbox')
    expect(input.className).toContain('w-full')
  })

  test('передает value и onChange', () => {
    const handleChange = jest.fn()
    render(<Input value="тест" onChange={handleChange} />)

    const input = screen.getByRole('textbox')
    expect(input).toHaveValue('тест')

    fireEvent.change(input, { target: { value: 'новый текст' } })
    expect(handleChange).toHaveBeenCalled()
  })

  test('input неактивен при disabled', () => {
    render(<Input disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  test('input имеет type text по умолчанию', () => {
    render(<Input />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'text')
  })

  test('input может иметь другой type', () => {
    render(<Input type="password" />)
    expect(screen.getByLabelText('input')).toHaveAttribute('type', 'password')
  })
})