document.addEventListener("DOMContentLoaded", () => {
    let i = 0;
    const jobText = 'IT Specialist';
    const speed = 100;

    const typeJob = () => {
        if (i < jobText.length) {
            document.getElementById("job").textContent += jobText.charAt(i++);
            setTimeout(typeJob, speed);
        }
    };
    setTimeout(typeJob, 1500);

    const COUNTER_KEY = 'visitorCounted';
    const VISITOR_COUNT_KEY = 'visitorCount';
    const visitorCountEl = document.getElementById('visitor-count');

    const displayCount = () => {
        const count = sessionStorage.getItem(VISITOR_COUNT_KEY) || '0';
        visitorCountEl.textContent = `Visitors: ${count}`;
    };

    if (!sessionStorage.getItem(COUNTER_KEY)) {
        fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/visitor')
        .then(res => res.text())
        .then(count => {
            sessionStorage.setItem(COUNTER_KEY, 'true');
            sessionStorage.setItem(VISITOR_COUNT_KEY, count);
            displayCount();
        })
        .catch(err => {
            console.error('Error fetching visitor count:', err);
            displayCount();
        });
    } else {
        displayCount();
    }
});