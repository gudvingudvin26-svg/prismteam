
class QuizTimer {
    constructor(seconds, onTick, onExpire) {
        this.seconds = seconds;
        this.remaining = seconds;
        this.onTick = onTick;
        this.onExpire = onExpire;
        this.interval = null;
    }

    start() {
        this.interval = setInterval(() => {
            this.remaining--;
            this.onTick(this.remaining);

            if (this.remaining <= 0) {
                this.stop();
                this.onExpire();
            }
        }, 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    reset(newSeconds) {
        this.stop();
        this.seconds = newSeconds || this.seconds;
        this.remaining = this.seconds;
    }
}

function updateTimerDisplay(seconds) {
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = seconds;

        // Меняем цвет когда мало времени
        if (seconds <= 5) {
            timerElement.classList.add('danger');
        } else {
            timerElement.classList.remove('danger');
        }
    }
}