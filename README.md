# Portal de Notícias - Jornal do Comercio

## Sobre o Projeto
Este projeto é uma **aplicação web** desenvolvida para o **Jornal do Comercio**, com o objetivo de oferecer uma **experiência moderna, interativa e intuitiva** para os usuários.  

O portal tem como foco **aumentar a fidelidade** e **o engajamento** do público, oferecendo notícias atualizadas, conteúdos relevantes e uma navegação otimizada.

---

## Funcionalidades
- Exibição de notícias com destaque, grid e página detalhada
- Busca por termo e filtro por tags
- Favoritar notícias (toggle) e ver lista de favoritos
- Feedbacks em notícias (nota 1-10 e comentário)
- Player de podcast ao vivo fixo no site
- Autenticação (login/registro) e conta do usuário

---

## Tecnologias
- Backend: Python 3.13, Django, Django ORM, django-ckeditor
- Frontend: HTML, CSS, JavaScript (vanilla), Font Awesome
- Banco: SQLite (dev/testes)
- Testes: Django TestCase/LiveServerTestCase, Selenium, pytest runner

---

## Executando localmente
  1) Crie a venv: `py -m venv .venv`
  2) Ative: `.venv\Scripts\activate`
  3) Instale dependências: `pip install -r requirements.txt`
  4) Aplique migrações: `python manage.py migrate`
  5) Rode servidor: `python manage.py runserver`
  6) Acesse: http://127.0.0.1:8000/

Testes automatizados: `python manage.py test`

---

## Deploy
[Site em produção](http://athenas-agb9hwgzb2cucacc.brazilsouth-01.azurewebsites.net/)

## Vídeo dos testes
https://youtu.be/mvB21_SKF_w

## Vídeo do Deploy:
https://youtu.be/BWUOTspWlZs
