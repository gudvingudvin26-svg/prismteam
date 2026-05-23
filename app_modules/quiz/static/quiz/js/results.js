
document.addEventListener('DOMContentLoaded', () => {
    animateScore();
    animateLeaderboard();
});

function animateScore() {
    const scoreElement = document.querySelector('.score-value');
    const finalScore = parseInt(scoreElement.textContent) || 0;
    let currentScore = 0;

    const interval = setInterval(() => {
        currentScore += Math.ceil(finalScore / 20);
        if (currentScore >= finalScore) {
            currentScore = finalScore;
            clearInterval(interval);
        }
        scoreElement.textContent = currentScore;
    }, 100);
}
function animateLeaderboard() {
    const rows = document.querySelectorAll('.leaderboard-table tbody tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';

        setTimeout(() => {
            row.style.transition = 'all 0.5s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, index * 100);
    });
}