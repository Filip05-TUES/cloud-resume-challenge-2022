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

  const updateCounterDisplay = (count) => {
    visitorCountEl.textContent = `Visitors: ${count}`;
    sessionStorage.setItem(VISITOR_COUNT_KEY, count);
  };

  const counted = sessionStorage.getItem(COUNTER_KEY);
  if (!counted) {
    fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/visitor', { method: 'POST' })
      .then(res => res.text())
      .then(count => {
        sessionStorage.setItem(COUNTER_KEY, 'true');
        updateCounterDisplay(count);
      })
      .catch(err => {
        console.error('Error counting visitor:', err);
        updateCounterDisplay(sessionStorage.getItem(VISITOR_COUNT_KEY) || '0');
      });
  } else {
    fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/visitor', { method: 'GET' })
      .then(res => res.text())
      .then(count => updateCounterDisplay(count))
      .catch(err => {
        console.error('Error fetching visitor count:', err);
        updateCounterDisplay(sessionStorage.getItem(VISITOR_COUNT_KEY) || '0');
      });
  }
});