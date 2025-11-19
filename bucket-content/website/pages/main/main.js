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
  const visitorCountEl = document.getElementById('visitor-count');

  if (!sessionStorage.getItem(COUNTER_KEY)) {
    fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/$default/visitor')
      .then(res => res.text())
      .then(count => {
        sessionStorage.setItem(COUNTER_KEY, 'true');
        visitorCountEl.textContent = `Visitors: ${count}`;
      })
      .catch(err => {
        console.error('Visitor counter error:', err);
      });
  }
});