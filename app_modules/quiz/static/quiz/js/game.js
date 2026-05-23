let currentQuestionIndex = 0;
let questions = [];
let timer = null;
let sessionId = null;

async function loadQuestions() {
    try {
        const response = await fetch(`/api/quiz/${quizId}/questions/`);
        const data = await response.json();
        questions = data.questions;
        document.getElementById('total-questions').textContent = questions.length;
        showQuestion(0);
    } catch (error) {
        console.error('Ошибка загрузки вопросов:', error);
        document.getElementById('question-text').textContent =
            'Ошибка загрузки. Обновите страницу.';
    }
}

function showQuestion(index) {
    if (index >= questions.length) {
        finishQuiz();
        return;
    }

    const question = questions[index];
    document.getElementById('question-text').textContent = question.text;
    document.getElementById('current-question').textContent = index + 1;


    const answersBlock = document.getElementById('answers-block');
    answersBlock.innerHTML = '';

    question.answers.forEach(answer => {
        const btn = document.createElement('button');
        btn.className = 'answer-btn';
        btn.textContent = answer.text;
        btn.onclick = () => submitAnswer(answer.id);
        answersBlock.appendChild(btn);
    });


    if (timer) {
        timer.reset(question.timer_seconds);
    } else {
        timer = new QuizTimer(
            question.timer_seconds,
            updateTimerDisplay,
            () => submitAnswer(null)
        );
    }
    timer.start();
}


async function submitAnswer(answerId) {
    if (timer) {
        timer.stop();
    }

    try {
        await fetch(`/api/quiz/${quizId}/answer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                session_id: sessionId,
                question_id: questions[currentQuestionIndex].id,
                answer_id: answerId
            })
        });

        currentQuestionIndex++;
        setTimeout(() => showQuestion(currentQuestionIndex), 500);
    } catch (error) {
        console.error('Ошибка отправки ответа:', error);
    }
}


function finishQuiz() {
    window.location.href = `/quiz/${quizId}/results/${sessionId}/`;
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    loadQuestions();
});