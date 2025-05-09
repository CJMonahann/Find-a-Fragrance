const textarea = document.getElementById('desc');
const form = document.getElementById('chatbox');

// Auto-grow textarea
textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
});

// Enter to submit, Shift+Enter to newline
textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        form.submit();
    }
});