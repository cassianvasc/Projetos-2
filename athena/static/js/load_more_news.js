document.addEventListener('DOMContentLoaded', function () {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const newsGrid = document.getElementById('newsGrid');
    if (!loadMoreBtn || !newsGrid) return;

    let loading = false;

    loadMoreBtn.addEventListener('click', function (e) {
        if (loading) return;
        loading = true;
        const originalText = loadMoreBtn.innerHTML;
        loadMoreBtn.innerHTML = 'Carregando... <i class="fas fa-spinner fa-spin"></i>';

        const existingIds = Array.from(newsGrid.querySelectorAll('.favorite-btn'))
            .map(b => b.dataset.id)
            .filter(Boolean);

        const excludeParam = existingIds.length ? `&exclude=${existingIds.join(',')}` : '';

        fetch(`/load-more-news/?${excludeParam}`)
            .then(res => {
                if (!res.ok) throw new Error('Falha ao carregar notícias');
                return res.json();
            })
            .then(data => {
                if (!data || !Array.isArray(data.noticias)) return;

                data.noticias.forEach(n => {
                    const article = document.createElement('article');
                    article.className = 'news-card';

                    const imgSrc = n.imagem || 'https://via.placeholder.com/400x250/cccccc/000000?text=Sem+Imagem';

                    article.innerHTML = `
                        <a href="/noticia/${n.id}/" class="news-card-link"></a>
                        <div class="news-content">
                            <div class="red-bar"></div>
                            <p class="news-excerpt">${escapeHtml(n.excerpt)}</p>
                            <button class="favorite-btn" data-id="${n.id}" aria-label="Adicionar aos favoritos">
                                <i class="far fa-heart"></i>
                            </button>
                        </div>
                        <div class="news-image">
                            <img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(n.titulo)}">
                        </div>
                    `;

                    newsGrid.appendChild(article);
                });

                if (!data.has_next) {
                    loadMoreBtn.style.display = 'none';
                }

            })
            .catch(err => {
                console.error('Erro ao carregar mais notícias:', err.message);
                alert('Não foi possível carregar mais notícias no momento.');
            })
            .finally(() => {
                loading = false;
                loadMoreBtn.innerHTML = originalText;
            });
    });

    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return String(unsafe)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
