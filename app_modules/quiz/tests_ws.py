"""Тесты WebSocket-консьюмера квизов и утилит таймеров Redis."""
import pytest
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from app_modules.quiz.consumers import QuizConsumer


@pytest.fixture
def quiz_communicator():
    """Фикстура: создаёт настроенный WebSocket-соединитель для QuizConsumer."""
    application = URLRouter([
        path('ws/quiz/test_quiz/', QuizConsumer.as_asgi()),
    ])
    return WebsocketCommunicator(application, 'ws/quiz/test_quiz/')


@pytest.mark.asyncio
async def test_websocket_connect(quiz_communicator):
    """Проверка успешного подключения к WebSocket."""
    connected, subprotocol = await quiz_communicator.connect()
    assert connected is True
    await quiz_communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_disconnect(quiz_communicator):
    """Проверка корректного закрытия WebSocket-соединения."""
    await quiz_communicator.connect()
    await quiz_communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_receive_message(quiz_communicator):
    """Проверка отправки и получения сообщений типа chat_message."""
    await quiz_communicator.connect()
    join_response = await quiz_communicator.receive_json_from()
    assert join_response['type'] == 'user_joined'
    await quiz_communicator.send_json_to({
        'type': 'chat_message',
        'message': 'Hello'
    })
    response = await quiz_communicator.receive_json_from()
    assert response['type'] == 'chat_message'
    assert response['message'] == 'Hello'
    await quiz_communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_invalid_json(quiz_communicator):
    """Проверка обработки невалидного JSON и возврата ошибки клиенту."""
    await quiz_communicator.connect()
    join_response = await quiz_communicator.receive_json_from()
    assert join_response['type'] == 'user_joined'
    await quiz_communicator.send_to('not valid json')
    response = await quiz_communicator.receive_json_from()
    assert response['type'] == 'error'
    assert 'Invalid JSON' in response['message']
    await quiz_communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_multiple_clients():
    """Проверка широковещательной рассылки сообщений между несколькими клиентами."""
    application = URLRouter([
        path('ws/quiz/broadcast_test/', QuizConsumer.as_asgi()),
    ])
    comm1 = WebsocketCommunicator(application, 'ws/quiz/broadcast_test/')
    comm2 = WebsocketCommunicator(application, 'ws/quiz/broadcast_test/')
    await comm1.connect()
    await comm1.receive_json_from()
    await comm2.connect()
    await comm2.receive_json_from()
    await comm1.send_json_to({
        'type': 'chat_message',
        'message': 'Broadcast test'
    })
    response1 = await comm1.receive_json_from()
    response2 = await comm2.receive_json_from()
    assert response2['type'] == 'chat_message'
    assert response2['message'] == 'Broadcast test'
    await comm1.disconnect()
    await comm2.disconnect()


@pytest.mark.asyncio
async def test_websocket_unknown_event_type(quiz_communicator):
    """Проверка обработки неизвестного типа события и возврата ошибки."""
    await quiz_communicator.connect()
    join_response = await quiz_communicator.receive_json_from()
    assert join_response['type'] == 'user_joined'
    await quiz_communicator.send_json_to({
        'type': 'unknown_event',
        'data': 'test'
    })
    response = await quiz_communicator.receive_json_from()
    assert response['type'] == 'error'
    await quiz_communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Redis not available in CI/CD")
async def test_redis_timer_start():
    """Проверка запуска таймера вопроса в Redis (пропускается в CI)."""
    from app_modules.quiz.redis_utils import get_timer_manager
    tm = get_timer_manager()
    end_time = tm.start_question_timer("quiz123", 1, 30)
    assert end_time > 0
    assert tm.is_timer_active("quiz123", 1) is True
    tm.stop_question_timer("quiz123", 1)


@pytest.mark.asyncio
@pytest.mark.skip(reason="Redis not available in CI/CD")
async def test_redis_timer_get_remaining():
    """Проверка получения оставшегося времени таймера в Redis (пропускается в CI)."""
    from app_modules.quiz.redis_utils import get_timer_manager
    tm = get_timer_manager()
    tm.start_question_timer("quiz456", 1, 30)
    timer = tm.get_question_timer("quiz456", 1)
    assert timer['active'] is True
    assert timer['remaining'] >= 0
    tm.stop_question_timer("quiz456", 1)