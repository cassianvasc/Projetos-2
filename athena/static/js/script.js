let currentPage = 1;

document.getElementById("loadMoreBtn").addEventListener("click", function () {
    currentPage++;

    fetch(`/load-more-news/?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            const grid = document.getElementById("newsGrid");

            data.noticias.forEach(n => {
                grid.innerHTML += `
                    <article class="news-card">
                        <div class="news-image">
                            <img src="${n.imagem ? n.imagem : 'https://via.placeholder.com/400x250'}">
                            ${n.tag ? `<span class="category-tag">${n.tag}</span>` : ""}
                        </div>
                        <div class="news-content">
                            <h3>${n.titulo}</h3>
                            <p class="news-meta"><i class="far fa-calendar"></i> ${n.data}</p>
                            <p class="news-excerpt">${n.excerpt}</p>
                            <a href="/noticia/${n.id}" class="read-more-btn">Ler mais</a>
                        </div>
                    </article>
                `;
            });

            if (!data.has_next) {
                document.getElementById("loadMoreBtn").style.display = "none";
            }
        });
});

//Parte de adicionar e remover notícias favoritas
const favoriteButtons = document.querySelectorAll('.favorite-btn');
const favoritesGrid = document.getElementById('favoritesGrid');

favoriteButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const noticiaId = btn.dataset.id;
        const heartIcon = btn.querySelector('i');
        const isFavorited = heartIcon.classList.contains('fas');
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
    });
});