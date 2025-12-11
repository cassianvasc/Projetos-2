// Gerenciador de Feedback (notícia e site)

document.addEventListener('DOMContentLoaded', function() {
    setupFeedbackForm('formFeedbackNoticia', 'mensagemFeedback', 'Enviar Feedback');
    setupFeedbackForm('formFeedbackSite', 'mensagemFeedbackSite', 'Enviar');
});

function setupFeedbackForm(formId, messageId, defaultBtnText) {
    const form = document.getElementById(formId);
    if (!form) return;

    const mensagemEl = document.getElementById(messageId);
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mensagemEl.textContent = data.message;
                mensagemEl.className = 'mensagem-feedback sucesso';
                mensagemEl.style.display = 'block';
                form.reset();
            } else {
                throw new Error('Erro ao enviar');
            }
        })
        .catch(() => {
            mensagemEl.textContent = 'Erro ao enviar feedback. Tente novamente.';
            mensagemEl.className = 'mensagem-feedback erro';
            mensagemEl.style.display = 'block';
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = defaultBtnText;
        });
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
