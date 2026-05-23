import React, { useState } from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button, Input, Card, Modal } from '../index'

describe('Integration Tests', () => {
  test('форма с input и кнопкой работает', () => {
    const handleSubmit = jest.fn()

    render(
      <form onSubmit={(e) => { e.preventDefault(); handleSubmit() }}>
        <Input label="Имя" data-testid="name-input" />
        <Button type="submit">Отправить</Button>
      </form>
    )

    const input = screen.getByTestId('name-input')
    fireEvent.change(input, { target: { value: 'Тест' } })
    expect(input).toHaveValue('Тест')

    fireEvent.click(screen.getByText('Отправить'))
    expect(handleSubmit).toHaveBeenCalled()
  })

  test('модалка с формой работает', () => {
    const TestComponent = () => {
      const [isOpen, setIsOpen] = useState(false)
      return (
        <>
          <Button onClick={() => setIsOpen(true)}>Открыть</Button>
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
            <Input label="Email" />
            <Button>Сохранить</Button>
          </Modal>
        </>
      )
    }

    render(<TestComponent />)

    // Модалка закрыта
    expect(screen.queryByText('Email')).not.toBeInTheDocument()

    // Открываем модалку
    fireEvent.click(screen.getByText('Открыть'))
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  test('карточка с кнопками работает', () => {
    render(
      <Card>
        <h3>Заголовок карточки</h3>
        <p>Описание</p>
        <Button variant="primary">Действие 1</Button>
        <Button variant="outline">Действие 2</Button>
      </Card>
    )

    expect(screen.getByText('Заголовок карточки')).toBeInTheDocument()
    expect(screen.getByText('Описание')).toBeInTheDocument()
    expect(screen.getByText('Действие 1')).toBeInTheDocument()
    expect(screen.getByText('Действие 2')).toBeInTheDocument()
  })

  test('валидация инпута с ошибкой', () => {
    const TestForm = () => {
      const [error, setError] = useState('')
      return (
        <div>
          <Input
            label="Пароль"
            error={error}
            onChange={(e) => {
              if (e.target.value.length < 6) {
                setError('Минимум 6 символов')
              } else {
                setError('')
              }
            }}
          />
          <Button>Отправить</Button>
        </div>
      )
    }

    render(<TestForm />)

    const input = screen.getByLabelText('Пароль')
    fireEvent.change(input, { target: { value: '123' } })
    expect(screen.getByText('Минимум 6 символов')).toBeInTheDocument()

    fireEvent.change(input, { target: { value: '123456' } })
    expect(screen.queryByText('Минимум 6 символов')).not.toBeInTheDocument()
  })
})