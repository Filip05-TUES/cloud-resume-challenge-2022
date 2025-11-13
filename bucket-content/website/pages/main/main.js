var imdex = 0;
var txtJob = 'IT Specialist';
var speed = 100;

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(function writeJob() {
        if (imdex < txtJob.length) {
            document.getElementById("job").innerHTML += txtJob.charAt(imdex);
            imdex++;
            setTimeout(writeJob, speed);
        }
    }, 1500);
});