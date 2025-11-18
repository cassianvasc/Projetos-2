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
