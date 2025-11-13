document.addEventListener("DOMContentLoaded", () => {
    history.scrollRestoration = 'manual';
    window.onbeforeunload = function() { window.scrollTo(0, 0); };
});