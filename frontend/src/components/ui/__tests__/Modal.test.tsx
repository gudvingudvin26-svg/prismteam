import { render, screen, fireEvent } from '@testing-library/react';
import { Modal } from '../index';

describe('Modal Component', () => {
  test('does not render when isOpen=false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        Контент модалки
      </Modal>
    );
    expect(screen.queryByText('Контент модалки')).not.toBeInTheDocument();
  });

  test('renders when isOpen=true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент модалки
      </Modal>
    );
    expect(screen.getByText('Контент модалки')).toBeInTheDocument();
  });

  test('displays title when provided', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Заголовок модалки">
        Контент
      </Modal>
    );
    expect(screen.getByText('Заголовок модалки')).toBeInTheDocument();
  });

  test('calls onClose when clicking overlay', () => {
    const handleClose = jest.fn();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        Контент
      </Modal>
    );

    const overlay = document.querySelector('.bg-gray-500.bg-opacity-75');
    fireEvent.click(overlay!);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  test('displays footer when provided', () => {
    render(
      <Modal
        isOpen={true}
        onClose={() => {}}
        footer={<button>Закрыть</button>}
      >
        Контент
      </Modal>
    );
    expect(screen.getByText('Закрыть')).toBeInTheDocument();
  });

  test('applies correct size sm', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} size="sm">
        Контент
      </Modal>
    );
    const modal = document.querySelector('.max-w-md');
    expect(modal).toBeInTheDocument();
  });

  test('applies correct size lg', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} size="lg">
        Контент
      </Modal>
    );
    const modal = document.querySelector('.max-w-2xl');
    expect(modal).toBeInTheDocument();
  });

  test('locks body scroll when open', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент
      </Modal>
    );
    expect(document.body.style.overflow).toBe('hidden');
  });

  test('unlocks body scroll when closed', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={() => {}}>
        Контент
      </Modal>
    );

    rerender(
      <Modal isOpen={false} onClose={() => {}}>
        Контент
      </Modal>
    );

    expect(document.body.style.overflow).toBe('unset');
  });
});