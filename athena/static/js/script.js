document.addEventListener("DOMContentLoaded", function () {
    // Event delegation para favoritos: funciona para botões estáticos e dinâmicos
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.favorite-btn');
        if (!btn) return;
        e.preventDefault();

        const noticiaId = btn.dataset.id;
        if (!noticiaId) return;

        fetch(`/favorite/notices/${noticiaId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 401) {
                // usuário não autenticado — redireciona para página que pede login
                const next = encodeURIComponent(window.location.pathname + window.location.search);
                window.location.href = `/need-login/?next=${next}`;
                // interrompe a cadeia
                throw new Error('not_authenticated');
            }
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (!data || !data.success) return;
            const icon = btn.querySelector('i');
            if (!icon) return;
            if (data.favorited) {
                icon.classList.remove('far', 'fa-heart');
                icon.classList.add('fas', 'fa-heart', 'filled');
                btn.classList.add('active');
            } else {
                icon.classList.remove('fas', 'fa-heart', 'filled');
                icon.classList.add('far', 'fa-heart');
                btn.classList.remove('active');
            }
        })
        .catch(err => console.warn('Erro ao favoritar:', err.message));
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
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const hamburger = document.querySelector('.hamburger-btn');
    const sidebarClose = document.querySelector('.sidebar__close');

    function openSidebar(){
        if (!sidebar || !sidebarOverlay) return;
        sidebar.classList.add('open');
        sidebar.setAttribute('aria-hidden','false');
        sidebarOverlay.classList.add('visible');
        sidebarOverlay.setAttribute('aria-hidden','false');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar(){
        if (!sidebar || !sidebarOverlay) return;
        sidebar.classList.remove('open');
        sidebar.setAttribute('aria-hidden','true');
        sidebarOverlay.classList.remove('visible');
        sidebarOverlay.setAttribute('aria-hidden','true');
        document.body.style.overflow = '';
    }

    hamburger?.addEventListener('click', openSidebar);
    sidebarOverlay?.addEventListener('click', closeSidebar);
    sidebarClose?.addEventListener('click', closeSidebar);
    // Delegated fallback: garante funcionamento mesmo se os elementos forem recriados
    document.addEventListener('click', (e) => {
        if (e.target.closest('.hamburger-btn')) {
            e.preventDefault();
            openSidebar();
        }
        if (e.target.closest('.sidebar__close')) {
            e.preventDefault();
            closeSidebar();
        }
        if (e.target === sidebarOverlay) {
            closeSidebar();
        }
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSidebar();
    });

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

// Busca status do podcast via API (se existir mini-player)
document.addEventListener('DOMContentLoaded', function () {
    const mini = document.getElementById('miniPodcast');
    const audio = document.getElementById('podcastAudio');
    const titleEl = document.getElementById('miniPodcastTitle');
    const liveBadge = document.getElementById('miniLiveBadge');

    if (!mini || !audio) return;

    // If template provided a stream URL or podcast id, try to attach it; otherwise show disabled message.
    const podcastId = mini.dataset.podcastId || mini.getAttribute('data-podcast-id');
    const streamUrlFromTemplate = mini.dataset.streamUrl || mini.getAttribute('data-stream-url');

    if (!podcastId && !streamUrlFromTemplate) {
        // No live podcast: disable controls and show message (markup already set by template)
        if (playBtn) playBtn.disabled = true;
        if (liveBadge) liveBadge.style.display = 'none';
    } else {
        // Prefer direct stream URL from template (fast), else query status API
        if (streamUrlFromTemplate) {
            attachStream(streamUrlFromTemplate);
        } else {
            const statusUrl = `/api/status/${podcastId}/`;
            fetch(statusUrl)
                .then(r => {
                    if (!r.ok) throw new Error('Status API não disponível');
                    return r.json();
                })
                .then(data => {
                    if (data.stream_url) {
                        attachStream(data.stream_url);
                    }

                    if (data.title && titleEl) {
                        titleEl.textContent = data.title;
                    }

                    if (data.is_live && liveBadge) {
                        liveBadge.style.display = 'inline-block';
                    }
                })
                .catch(err => {
                    console.info('Podcast status fetch failed:', err.message);
                });
        }
    }

    // helper: carregar hls.js dinamicamente se necessário
    function loadHlsJs(cb) {
        if (window.Hls) return cb();
        const s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
        s.onload = cb;
        s.onerror = () => console.warn('Falha ao carregar hls.js');
        document.head.appendChild(s);
    }

    // attachStream: suporta .m3u8 via hls.js ou nativo, e streams diretos (mp3)
    function attachStream(src) {
        if (!src) return;
        // se for HLS
        const isHls = src.split('?')[0].toLowerCase().endsWith('.m3u8');

        if (isHls) {
            if (audio.canPlayType('application/vnd.apple.mpegurl')) {
                audio.src = src;
                audio.load();
            } else {
                loadHlsJs(() => {
                    if (window.Hls && Hls.isSupported()) {
                        try {
                            const hls = new Hls();
                            hls.loadSource(src);
                            hls.attachMedia(audio);
                        } catch (e) {
                            console.warn('Erro ao inicializar hls.js', e);
                        }
                    } else {
                        console.warn('HLS não suportado neste navegador');
                    }
                });
            }
        } else {
            // stream direto (mp3, etc.)
            audio.src = src;
            audio.load();
        }
    }

    // --- CONTROLES DO PLAYER (play/pause, progresso, tempo) ---
    const playBtn = document.getElementById('podPlayBtn');
    const progress = document.getElementById('podProgress');
    const progressFilled = document.getElementById('podProgressFilled');
    const currentTimeEl = document.getElementById('podCurrent');

    function formatTime(sec) {
        if (!isFinite(sec)) return '0:00';
        const minutes = Math.floor(sec / 60);
        const seconds = Math.floor(sec % 60).toString().padStart(2, '0');
        return minutes + ':' + seconds;
    }

    if (playBtn) {
        playBtn.addEventListener('click', function () {
            if (audio.paused) {
                audio.play().catch(err => console.warn('Play failed:', err.message));
                this.querySelector('i')?.classList.remove('fa-play');
                this.querySelector('i')?.classList.add('fa-pause');
            } else {
                audio.pause();
                this.querySelector('i')?.classList.remove('fa-pause');
                this.querySelector('i')?.classList.add('fa-play');
            }
        });
    }

    // atualizar progresso e tempo
    audio.addEventListener('timeupdate', function () {
        const percent = (audio.currentTime / audio.duration) * 100 || 0;
        if (progressFilled) progressFilled.style.width = percent + '%';
        if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
    });

    // permitir seek clicando na barra
    if (progress) {
        progress.addEventListener('click', function (e) {
            if (!isFinite(audio.duration) || audio.duration === 0) return;
            const rect = this.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const pct = clickX / rect.width;
            audio.currentTime = pct * audio.duration;
        });
    }
});