let websocket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
    try {
        websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
            console.log('WebSocket подключен');
            reconnectAttempts = 0;
        };

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        websocket.onerror = (error) => {
            console.error('WebSocket ошибка:', error);
        };

        websocket.onclose = () => {
            console.log('WebSocket закрыт');
            attemptReconnect();
        };
    } catch (error) {
        console.error('Ошибка подключения WebSocket:', error);
        attemptReconnect();
    }
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'new_question':
            handleNewQuestion(data);
            break;
        case 'timer_update':
            handleTimerUpdate(data);
            break;
        case 'quiz_finished':
            handleQuizFinished(data);
            break;
    }
}

function handleNewQuestion(data) {
    if (timer) {
        timer.reset(data.timer_seconds);
        timer.start();
    }
}

function handleTimerUpdate(data) {
    updateTimerDisplay(data.seconds);
}

function handleQuizFinished(data) {
    if (timer) {
        timer.stop();
    }
    window.location.href = data.results_url;
}

function attemptReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        setTimeout(() => {
            console.log(`Попытка ${reconnectAttempts}/${maxReconnectAttempts}`);
            connectWebSocket();
        }, 2000 * reconnectAttempts);
    }
}
function sendWebSocketMessage(message) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(message));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
});