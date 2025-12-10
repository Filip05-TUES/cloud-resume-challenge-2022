document.addEventListener("DOMContentLoaded", () => {
    const COUNTER_KEY = 'visitorCounted';
    const VISITOR_COUNT_KEY = 'visitorCount';
    const visitorCountEl = document.getElementById('visitor-count');

    const updateCounterDisplay = (count) => {
        visitorCountEl.textContent = `Visitors: ${count}`;
        localStorage.setItem(VISITOR_COUNT_KEY, count);
    };

    const counted = localStorage.getItem(COUNTER_KEY);
    if (!counted) {
        fetch('https://dzinfmbutk.execute-api.us-east-1.amazonaws.com/prod/visitor', { method: 'POST' })
        .then(res => res.text())
        .then(count => {
            localStorage.setItem(COUNTER_KEY, 'true');
            updateCounterDisplay(count);
        })
        .catch(err => {
            console.error('Error counting visitor:', err);
            updateCounterDisplay(localStorage.getItem(VISITOR_COUNT_KEY) || '0');
        });
    } else {
        fetch('https://dzinfmbutk.execute-api.us-east-1.amazonaws.com/prod/visitor', { method: 'GET' })
        .then(res => res.text())
        .then(count => updateCounterDisplay(count))
        .catch(err => {
            console.error('Error fetching visitor count:', err);
            updateCounterDisplay(localStorage.getItem(VISITOR_COUNT_KEY) || '0');
        });
    }
});