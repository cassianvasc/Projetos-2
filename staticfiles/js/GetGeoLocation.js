function getLocationAndSend() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const data = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };

            // Armazenar localmente (opcional)
            localStorage.setItem('user_location', JSON.stringify(data));

            // Enviar para o servidor via fetch
            fetch('/set-location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Django CSRF
                },
                body: JSON.stringify(data)
            });
        });
    } else {
        alert("Geolocalização não suportada pelo seu navegador.");
    }
}

// Função para pegar o CSRF token
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

// Chamar a função ao carregar a página
window.onload = getLocationAndSend;