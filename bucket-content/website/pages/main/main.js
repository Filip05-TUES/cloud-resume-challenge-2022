document.addEventListener("DOMContentLoaded", () => {
  console.log('Part 1');
  let imdex = 0;
  const txtJob = 'IT Specialist';
  const speed = 100;

  setTimeout(function writeJob() {
    if (imdex < txtJob.length) {
      document.getElementById("job").innerHTML += txtJob.charAt(imdex);
      imdex++;
      setTimeout(writeJob, speed);
    }
  }, 1500);
  console.log('Part 2');

  const COUNTER_KEY = 'visitorCounted';
  const visitorCountEl = document.getElementById('visitor-count');

  if (!sessionStorage.getItem(COUNTER_KEY)) {
    console.log('New visitor!');
    fetch('https://hdqdi664jd.execute-api.us-east-1.amazonaws.com/$default/visitor', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(currentViews => {
        sessionStorage.setItem(COUNTER_KEY, 'true');
        visitorCountEl.textContent = `Visitors: ${currentViews}`;
      })
      .catch(err => {
        console.error('Error counting visitor:', err);
      });
  } else {
    console.log('Error');
  }
});