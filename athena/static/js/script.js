document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".favorite-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function () {
            const noticiaId = this.dataset.id;

            fetch(`/favorite/notices/${noticiaId}/`,{
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) return;

                const icon = this.querySelector("i");

                if (data.favorited) {
                    icon.classList.remove("far", "fa-heart");
                    icon.classList.add("fas", "fa-heart", "filled");
                } else {
                    icon.classList.remove("fas", "fa-heart", "filled");
                    icon.classList.add("far", "fa-heart");
                }
            });
        });
    });

    // pegar CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const sections = Array.from(document.querySelectorAll("section[id]"));
    const navLinksAll = Array.from(document.querySelectorAll(".nav-menu a"));
    const hashLinks = navLinksAll.filter(a => a.getAttribute("href")?.startsWith("#"));
    const homeLink = navLinksAll.find(a => !(a.getAttribute("href") || "").startsWith("#")) || navLinksAll[0];

    function clearActive() {
        navLinksAll.forEach(l => l.classList.remove("active"));
    }

    function setActiveLinkForSection(sectionId) {
        clearActive();
        const activeLink = document.querySelector('.nav-menu a[href="#' + sectionId + '"]');
        if (activeLink) {
            activeLink.classList.add("active");
        } else if (homeLink) {
            // fallback: se nenhuma âncora bate, marca home
            homeLink.classList.add("active");
        }
    }

    function changeActive() {
        const scrollPos = window.scrollY + 300;
        let found = false;

        for (const section of sections) {
            const top = section.offsetTop;
            const bottom = top + section.offsetHeight;
            if (scrollPos >= top && scrollPos < bottom) {
                setActiveLinkForSection(section.id);
                found = true;
                break;
            }
        }

        if (!found) {
            // se não está em nenhuma seção (topo ou área sem seção), marca home
            clearActive();
            if (homeLink) homeLink.classList.add("active");
        }
    }

    // smooth scroll para links de hash e proteção caso o alvo não exista
    hashLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            const href = this.getAttribute("href");
            const targetId = href && href.startsWith("#") ? href.slice(1) : null;
            const target = targetId ? document.getElementById(targetId) : null;

            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
                // atualiza active imediatamente
                setActiveLinkForSection(targetId);
            } else {
                // se não existir target, deixa o comportamento padrão (ou previne se preferir)
                console.warn("Anchor target not found:", href);
            }
        });
    });

    // também altera active ao clicar em links que levam pra outras páginas (opcional)
    navLinksAll.forEach(link => {
        link.addEventListener("click", function () {
            // se for link para hash, o handler acima já cuida
            if (!(this.getAttribute("href") || "").startsWith("#")) {
                clearActive();
                this.classList.add("active");
            }
        });
    });

    // Listener de scroll
    window.addEventListener("scroll", changeActive, { passive: true });

    // Set initial state
    changeActive();
});