import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Modal } from '../index'

describe('Modal Component', () => {
  test('не рендерится когда isOpen=false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        Контент модалки
      </Modal>
    )
    expect(screen.queryByText('Контент модалки')).not.toBeInTheDocument()
  })

  test('рендерится когда isOpen=true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент модалки
      </Modal>
    )
    expect(screen.getByText('Контент модалки')).toBeInTheDocument()
  })

  test('отображает заголовок когда передан', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Заголовок модалки">
        Контент
      </Modal>
    )
    expect(screen.getByText('Заголовок модалки')).toBeInTheDocument()
  })

  test('вызывает onClose при клике на оверлей', () => {
    const handleClose = jest.fn()
    render(
      <Modal isOpen={true} onClose={handleClose}>
        Контент
      </Modal>
    )

    const overlay = document.querySelector('.bg-gray-500.bg-opacity-75')
    fireEvent.click(overlay!)
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  test('отображает footer когда передан', () => {
    render(
      <Modal
        isOpen={true}
        onClose={() => {}}
        footer={<button>Закрыть</button>}
      >
        Контент
      </Modal>
    )
    expect(screen.getByText('Закрыть')).toBeInTheDocument()
  })

  test('применяет правильный размер sm', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} size="sm">
        Контент
      </Modal>
    )
    const modal = document.querySelector('.max-w-md')
    expect(modal).toBeInTheDocument()
  })

  test('применяет правильный размер lg', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} size="lg">
        Контент
      </Modal>
    )
    const modal = document.querySelector('.max-w-2xl')
    expect(modal).toBeInTheDocument()
  })

  test('блокирует скролл body когда открыт', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент
      </Modal>
    )
    expect(document.body.style.overflow).toBe('hidden')
  })

  test('возвращает скролл когда закрыт', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент
      </Modal>
    )

    rerender(
      <Modal isOpen={false} onClose={() => {}}>
        Контент
      </Modal>
    )

    expect(document.body.style.overflow).toBe('unset')
  })
})