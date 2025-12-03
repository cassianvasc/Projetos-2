document.addEventListener('DOMContentLoaded', function () {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const newsGrid = document.getElementById('newsGrid');
    if (!loadMoreBtn || !newsGrid) return;

    let page = 2; // first page already rendered server-side
    let loading = false;

    loadMoreBtn.addEventListener('click', function (e) {
        if (loading) return;
        loading = true;
        const originalText = loadMoreBtn.innerHTML;
        loadMoreBtn.innerHTML = 'Carregando... <i class="fas fa-spinner fa-spin"></i>';

        // collect IDs already displayed to avoid duplicates
        const existingIds = Array.from(newsGrid.querySelectorAll('.favorite-btn'))
            .map(b => b.dataset.id)
            .filter(Boolean);

        const excludeParam = existingIds.length ? `&exclude=${existingIds.join(',')}` : '';

        fetch(`/load-more-news/?page=${page}${excludeParam}`)
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
                    const tagHtml = n.tag ? `<span class="category-tag">${escapeHtml(n.tag)}</span>` : '';

                    article.innerHTML = `
                        <div class="news-image">
                            <img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(n.titulo)}">
                            ${tagHtml}
                        </div>
                        <div class="news-content">
                            <h3 class="news-title">${escapeHtml(n.titulo)}</h3>
                            <p class="news-meta">
                                <span><i class="far fa-calendar"></i> ${escapeHtml(n.data)}</span>
                                ${n.autor ? `<span><i class="far fa-user"></i> Por ${escapeHtml(n.autor)}</span>` : ''}
                            </p>
                            <p class="news-excerpt">${escapeHtml(n.excerpt)}</p>

                            <a name="${n.id}" href="/noticia/${n.id}/" class="read-more-btn">Ler mais <i class="fas fa-arrow-right"></i></a>

                            <button class="favorite-btn" data-id="${n.id}" aria-label="Adicionar aos favoritos">
                                <i class="far fa-heart"></i>
                            </button>
                        </div>
                    `;

                    newsGrid.appendChild(article);
                });

                if (!data.has_next) {
                    loadMoreBtn.style.display = 'none';
                } else {
                    page += 1;
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
