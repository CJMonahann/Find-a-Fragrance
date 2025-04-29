const bars = document.querySelectorAll('.hello')

bars.forEach(bar => {
    const percent = bar.dataset.per;
    bar.style.width = percent + '%';
});