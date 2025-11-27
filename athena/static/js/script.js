function toggleFavorite(e) {
    const btn = e.currentTarget;
    const noticiaId = btn.dataset.id;
    const heartIcon = btn.querySelector('i');
    const isFavorited = heartIcon.classList.contains('fas');
    const favoritesGrid = document.getElementById('favoritesGrid');

    if (isFavorited) {
        heartIcon.classList.remove('fas');
        heartIcon.classList.add('far');

        const favItem = favoritesGrid.querySelector(`[data-id="${noticiaId}"]`);
        if (favItem) favItem.remove();

        if (favoritesGrid.children.length === 0) {
            const p = document.createElement('p');
            p.className = 'no-favorites';
            p.textContent = "Você ainda não possui notícias favoritas. Clique no ❤ para adicionar!";
            favoritesGrid.appendChild(p);
        }
    } else {
        heartIcon.classList.remove('far');
        heartIcon.classList.add('fas');

        const noFav = favoritesGrid.querySelector('.no-favorites');
        if (noFav) noFav.remove();

        const noticiaCard = btn.closest('.news-card').cloneNode(true);
        noticiaCard.dataset.id = noticiaId;
        noticiaCard.querySelector('.favorite-btn').remove();
        favoritesGrid.appendChild(noticiaCard);
    }
}

document.getElementById("loadMoreBtn").addEventListener("click", function () {
    currentPage++;
    fetch(`/load-more-news/?page=${currentPage}`)
        .then(res => res.json())
        .then(data => {
            const grid = document.getElementById("newsGrid");

            data.noticias.forEach(n => {
                const article = document.createElement('article');
                article.className = 'news-card';
                article.innerHTML = `
                    <div class="news-image">
                        <img src="${n.imagem ? n.imagem : 'https://via.placeholder.com/400x250'}">
                        ${n.tag ? `<span class="category-tag">${n.tag}</span>` : ""}
                    </div>
                    <div class="news-content">
                        <h3>${n.titulo}</h3>
                        <p class="news-meta"><i class="far fa-calendar"></i> ${n.data}</p>
                        <p class="news-excerpt">${n.excerpt}</p>
                        <a href="/noticia/${n.id}" class="read-more-btn">Ler mais</a>
                        <button class="favorite-btn" data-id="${n.id}" aria-label="Adicionar aos favoritos">
                            <i class="far fa-heart"></i>
                        </button>
                    </div>
                `;
                grid.appendChild(article);

                article.querySelector('.favorite-btn').addEventListener('click', toggleFavorite);
            });

            if (!data.has_next) document.getElementById("loadMoreBtn").style.display = "none";
        });
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.favorite-btn').forEach(btn => btn.addEventListener('click', toggleFavorite));

    const linkInicio = document.querySelector('.nav-menu a[href="/"]');
    const linkFavoritos = document.querySelector('.nav-menu a[href="#favoritos"]');
    const favoritosSection = document.getElementById('favoritos');
    const offset = 120;

    function updateActiveMenu() {
        const scrollPos = window.scrollY || window.pageYOffset;
        const favoritosTop = favoritosSection.offsetTop - offset;
        const favoritosBottom = favoritosTop + favoritosSection.offsetHeight;

        if (scrollPos >= favoritosTop && scrollPos < favoritosBottom) {
            linkFavoritos.classList.add('active');
            linkInicio.classList.remove('active');
        } else {
            linkFavoritos.classList.remove('active');
            linkInicio.classList.add('active');
        }
    }

    window.addEventListener('scroll', updateActiveMenu);
    window.addEventListener('resize', updateActiveMenu);
    window.addEventListener('load', updateActiveMenu);

    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => setTimeout(updateActiveMenu, 100));
    });
});
