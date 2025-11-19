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

  if (!localStorage.getItem(COUNTER_KEY)) {
    fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/visitor', {
      method: 'GET'
    })
      .then(res => res.text())
      .then(count => {
        localStorage.setItem(COUNTER_KEY, 'true');
        localStorage.setItem(VISITOR_COUNT_KEY, count);
        visitorCountEl.textContent = `Visitors: ${count}`;
      })
      .catch(err => {
        console.error('Error counting visitor:', err);
        visitorCountEl.textContent = `Visitors: 0`;
      });
  } else {
    const count = localStorage.getItem(VISITOR_COUNT_KEY) || '0';
    visitorCountEl.textContent = `Visitors: ${count}`;
  }
});