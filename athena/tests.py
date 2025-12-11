from django.test import TestCase,LiveServerTestCase,override_settings
from Jornalista.models import Perfil as perfilJornalista
from .models import Perfil as perfilUsuario
from selenium.webdriver.common.action_chains import ActionChains
from django.contrib.auth.models import User
from django.urls import reverse
from Jornalista.models import *
from .models import *
from Podcast_Player.models import LivePodcast
import time
from unittest.mock import patch, MagicMock

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .models import *

@override_settings(
    DEBUG=True,
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
)
class TesteE2E(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')        
        options.add_argument("--disable-infobars")
        options.add_argument("--incognito")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})

        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service,options=options)
        cls.browser.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.browser.quit()
        except Exception:
            pass
        super().tearDownClass()


    def login(self, username='teste', password='123', create_user=True):
        self.browser.delete_all_cookies()

        if create_user:
            user = User.objects.create_user(username=username, password=password)
            perfil = Perfil.objects.create(user=user)
            self.assertEqual(perfil.user.username, username)
        else:
            user = User.objects.get(username=username)

        self.browser.get(f'{self.live_server_url}/login/')

        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.send_keys(username)
        passwordInput.send_keys(password)
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        return user

    def test_login(self):
        self.browser.delete_all_cookies()

        self.browser.get(f'{self.live_server_url}/register/')

        self.assertIn('Já tem uma conta?',self.browser.page_source)

        usernameInput = self.browser.find_element(By.NAME,'username')
        emailInput = self.browser.find_element(By.NAME,'email')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.send_keys('teste')
        emailInput.send_keys('a@gmail.com')
        passwordInput.send_keys('Abc123!')
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,"username"))
        )

        time.sleep(1)
        
        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.send_keys('Erro')
        passwordInput.send_keys('Abc123!')
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), "Nome de usuario/email ou senha incorreto")
        )

        time.sleep(0.5)
        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.clear()
        passwordInput.clear()
        
        usernameInput.send_keys('teste')
        passwordInput.send_keys('Abc123!')
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

    def test_tags(self):
        user = self.login()

        futebolTag = Tag.objects.create(nome='Futebol')
        politicaTag = Tag.objects.create(nome='Politica')

        button = self.browser.find_element(By.NAME,"user")
        button.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/user/')
        )

        futebolButton = self.browser.find_element(By.XPATH, "//label[.//span[text()='Futebol']]")
        politicaButton = self.browser.find_element(By.XPATH, "//label[.//span[text()='Politica']]")
        saveButton = self.browser.find_element(By.NAME,"save")

        futebolButton.click()
        politicaButton.click()
        saveButton.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'context'))
        )

        self.assertEqual(user.perfil.tags.count(), 2)

        futebolButton = self.browser.find_element(By.XPATH, "//label[.//span[text()='Futebol']]")
        saveButton = self.browser.find_element(By.NAME,"save")

        futebolButton.click()
        saveButton.click()
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'context'))
        )
        time.sleep(0.5)
        user.perfil.refresh_from_db()
        self.assertEqual(user.perfil.tags.count(),1)


    def test_noticias_por_tag_slug_invalido(self):
        self.browser.get(f'{self.live_server_url}/tag/tag-que-nao-existe/')
        
        WebDriverWait(self.browser, 10).until(
            lambda driver: "404" in driver.page_source or "Not Found" in driver.page_source or "Não encontrado" in driver.page_source
        )


    def test_noticias_por_tag_filtra_corretamente(self):

        user = User.objects.create_user(username='jornalistaTeste')
        jornalista = perfilJornalista.objects.create(user=user)

        self.tag_politica = Tag.objects.create(nome='Política Local')
        self.tag_economia = Tag.objects.create(nome='Economia')
        
        self.noticia_a = Noticia.objects.create(autor=jornalista,titulo='Título A', conteudo='Conteúdo A')
        self.noticia_b = Noticia.objects.create(autor=jornalista,titulo='Título B', conteudo='Conteúdo B')
        self.noticia_c = Noticia.objects.create(autor=jornalista,titulo='Título C', conteudo='Conteúdo C')
        
        self.noticia_a.tags.add(self.tag_politica) 
        self.noticia_b.tags.add(self.tag_politica, self.tag_economia)
        self.noticia_c.tags.add(self.tag_economia)

        self.browser.get(f'{self.live_server_url}/tag/{self.tag_politica.slug}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(1)
        
        page_source = self.browser.page_source
        
        self.assertIn('Título A', page_source)
        self.assertIn('Título B', page_source)
        self.assertNotIn('Título C', page_source)
        
        self.browser.get(f'{self.live_server_url}/tag/{self.tag_economia.slug}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(1)
        
        page_source = self.browser.page_source
        
        self.assertIn('Título B', page_source)
        self.assertIn('Título C', page_source)
        self.assertNotIn('Título A', page_source)

    def test_pesquisa_noticia(self):

        user = User.objects.create_user(username='jornalistaTeste')
        jornalista = perfilJornalista.objects.create(user=user)

        self.noticia_a = Noticia.objects.create(autor=jornalista,titulo='Título A', conteudo='Conteúdo A')

        self.browser.get(f'{self.live_server_url}/')

        hamburger_btn = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, "hamburger-btn"))
        )
        hamburger_btn.click()
        
        time.sleep(0.5)
        WebDriverWait(self.browser, 10).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, "sidebar-search"))
        )

        search = self.browser.find_element(By.NAME,"BarraDePesquisa")
        search.send_keys("Título A")
        
        searchButton = self.browser.find_element(By.CLASS_NAME,"sidebar-search-btn")
        searchButton.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/pesquisa/')
        )

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Título A')]"))
        )

        self.browser.get(f'{self.live_server_url}/')

        hamburger_btn = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, "hamburger-btn"))
        )
        hamburger_btn.click()
        
        time.sleep(0.5)
        WebDriverWait(self.browser, 10).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, "sidebar-search"))
        )

        search = self.browser.find_element(By.NAME,"BarraDePesquisa")
        search.send_keys("nada")
        searchButton = self.browser.find_element(By.CLASS_NAME,"sidebar-search-btn")
        searchButton.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/pesquisa/')
        )

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Não há notícias relacionadas')]"))
        )

    def test_add_noticia_jornalista(self):
        username = 'jornalista_add'
        password = 'Senha123!'
        user = User.objects.create_user(username=username, password=password)
        perfil = Perfil.objects.create(user=user)
        jornalista = perfilJornalista.objects.create(user=user)

        self.login(username=username, password=password, create_user=False)
        
        self.browser.get(f'{self.live_server_url}/add/noticia')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, 'titulo'))
        )
        
        titulo_input = self.browser.find_element(By.NAME, 'titulo')
        regiao_input = self.browser.find_element(By.NAME, 'regiao')
        conteudo_input = self.browser.find_element(By.NAME, 'conteudo')
        
        titulo_input.send_keys('Teste E2E - Nova Notícia')
        regiao_input.send_keys('Recife')
        conteudo_input.send_keys('Conteúdo de teste para a nova notícia criada pelo E2E.')
        
        submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_matches(f'{self.live_server_url}/$')
        )
        
        from Jornalista.models import Noticia
        self.assertTrue(Noticia.objects.filter(titulo='Teste E2E - Nova Notícia').exists())
        noticia = Noticia.objects.get(titulo='Teste E2E - Nova Notícia')
        self.assertEqual(noticia.autor, jornalista)

    def test_add_noticia_with_tags(self):
        username = 'jornalista_tags'
        password = 'Senha123!'
        user = User.objects.create_user(username=username, password=password)
        perfil = Perfil.objects.create(user=user)
        jornalista = perfilJornalista.objects.create(user=user)

        tag1 = Tag.objects.create(nome='Política')
        tag2 = Tag.objects.create(nome='Economia')

        self.login(username=username, password=password, create_user=False)
        
        self.browser.get(f'{self.live_server_url}/add/noticia')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, 'titulo'))
        )
        
        titulo_input = self.browser.find_element(By.NAME, 'titulo')
        regiao_input = self.browser.find_element(By.NAME, 'regiao')
        conteudo_input = self.browser.find_element(By.NAME, 'conteudo')
        
        titulo_input.send_keys('Teste Tags')
        regiao_input.send_keys('Recife')
        conteudo_input.send_keys('Conteúdo com tags para teste.')
        
        tags_select = Select(self.browser.find_element(By.NAME, 'tags'))
        tags_select.select_by_visible_text('Política')
        tags_select.select_by_visible_text('Economia')
        
        submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_matches(f'{self.live_server_url}/$')
        )
        
        from Jornalista.models import Noticia
        noticia = Noticia.objects.filter(titulo='Teste Tags').first()
        self.assertIsNotNone(noticia)
        tag_names = set([t.nome for t in noticia.tags.all()])
        self.assertTrue('Política' in tag_names and 'Economia' in tag_names)

    def test_podcast_live_shows_on_home(self):
        
        if LivePodcast is None:
            self.skipTest('Podcast_Player app not available')

        lp = LivePodcast.objects.create(title='Ao Vivo - Teste', stream_url='https://example.com/stream.mp3', is_live=True)

        self.browser.get(f'{self.live_server_url}/')

        mini = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'miniPodcast'))
        )

        title_el = self.browser.find_element(By.ID, 'miniPodcastTitle')
        self.assertIn('Ao Vivo - Teste', title_el.text)

        live_badge = self.browser.find_element(By.CLASS_NAME, 'live-badge')
        self.assertTrue(live_badge.is_displayed())

    def test_favoritar_noticia_autenticado(self):
        jornalista_user = User.objects.create_user(username='journ_fav', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia Favorita', conteudo='Conteudo')

        user = User.objects.create_user(username='user_fav', password='pwd')
        perfil = perfilUsuario.objects.create(user=user)

        self.login(username='user_fav', password='pwd', create_user=False)
        
        self.browser.get(f'{self.live_server_url}/noticia/{noticia.id}/')
        
        favorite_btn = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'favorite-btn'))
        )
        
        favorite_btn.click()
        
        time.sleep(1)
        
        perfil.refresh_from_db()
        self.assertTrue(perfil.relevantes.filter(id=noticia.id).exists())
        
        favorite_btn.click()
        time.sleep(1)
        
        perfil.refresh_from_db()
        self.assertFalse(perfil.relevantes.filter(id=noticia.id).exists())

    def test_favoritar_noticia_sem_login(self):
        jornalista_user = User.objects.create_user(username='journ_fav2', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia Sem Login', conteudo='Conteudo')

        self.browser.delete_all_cookies()
        self.browser.get(f'{self.live_server_url}/noticia/{noticia.id}/')
        
        favorite_btn = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'favorite-btn'))
        )
        
        favorite_btn.click()
        time.sleep(1)
        
        resp = self.client.post(f'/favorite/notices/{noticia.id}/')
        self.assertEqual(resp.status_code, 401)

    def test_feedback_noticia_usuario_com_login(self):

        jornalista_user = User.objects.create_user(username='journ_h6_1', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia H6', conteudo='Conteudo importante')

        user = User.objects.create_user(username='user_h6_1', password='pwd')
        perfil = perfilUsuario.objects.create(user=user)

        self.login(username='user_h6_1', password='pwd', create_user=False)
        
        self.browser.get(f'{self.live_server_url}/noticia/{noticia.id}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'formFeedbackNoticia'))
        )
        
        rating_9 = self.browser.find_element(By.XPATH, "//input[@name='avaliacao'][@value='9']")
        rating_9.click()
        
        comentario_input = self.browser.find_element(By.ID, 'id_comentario')
        comentario_input.send_keys('Notícia muito relevante e bem escrita')
        
        submit_btn = self.browser.find_element(By.CLASS_NAME, 'btn-enviar-feedback')
        submit_btn.click()
        
        time.sleep(1)
        
        self.assertEqual(Feedback.objects.filter(noticia=noticia, tipo='noticia').count(), 1)
        feedback = Feedback.objects.get(noticia=noticia, tipo='noticia')
        self.assertEqual(feedback.avaliacao, 9)
        self.assertEqual(feedback.usuario, user)

    def test_feedback_noticia_usuario_sem_login(self):

        jornalista_user = User.objects.create_user(username='journ_h6_3', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia H6 Sem Login', conteudo='Conteudo')

        self.browser.delete_all_cookies()
        self.browser.get(f'{self.live_server_url}/noticia/{noticia.id}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'formFeedbackNoticia'))
        )
        
        rating_5 = self.browser.find_element(By.XPATH, "//input[@name='avaliacao'][@value='5']")
        rating_5.click()
        
        comentario_input = self.browser.find_element(By.ID, 'id_comentario')
        comentario_input.send_keys('Feedback sem login')
        
        submit_btn = self.browser.find_element(By.CLASS_NAME, 'btn-enviar-feedback')
        submit_btn.click()
        
        time.sleep(1)
        
        feedback_count = Feedback.objects.filter(noticia=noticia).count()
        if feedback_count > 0:
            fb = Feedback.objects.get(noticia=noticia)
            self.assertIsNone(fb.usuario)

    def test_feedback_noticia_avaliacoes_multiplas(self):

        jornalista_user = User.objects.create_user(username='journ_multi_fb', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia Multi Feedback', conteudo='Conteudo')

        avaliacoes = [8, 6, 9]
        
        for i in range(3):
            user = User.objects.create_user(username=f'user_multi_fb_{i}', password='pwd')
            perfil = perfilUsuario.objects.create(user=user)

            self.login(username=f'user_multi_fb_{i}', password='pwd', create_user=False)
            
            self.browser.get(f'{self.live_server_url}/noticia/{noticia.id}/')
            
            WebDriverWait(self.browser, 10).until(
                expected_conditions.presence_of_element_located((By.ID, 'formFeedbackNoticia'))
            )
            
            rating = self.browser.find_element(By.XPATH, f"//input[@name='avaliacao'][@value='{avaliacoes[i]}']")
            rating.click()
            
            comentario_input = self.browser.find_element(By.ID, 'id_comentario')
            comentario_input.send_keys(f'Feedback {i+1}')
            
            submit_btn = self.browser.find_element(By.CLASS_NAME, 'btn-enviar-feedback')
            submit_btn.click()
            
            time.sleep(1)

        feedbacks = Feedback.objects.filter(noticia=noticia, tipo='noticia')
        self.assertEqual(feedbacks.count(), 3)
        
        notas = sorted([fb.avaliacao for fb in feedbacks])
        self.assertEqual(notas, [6, 8, 9])

    def test_feedback_noticia_autor_visualiza(self):

        jornalista_user = User.objects.create_user(username='journ_view_fb_h6', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        perfilJornalista_perfil = perfilJornalista.objects.get(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia Ver Feedback', conteudo='Conteudo')

        user1 = User.objects.create_user(username='user_fb_1', password='pwd')
        perfilUsuario.objects.create(user=user1)
        Feedback.objects.create(tipo='noticia', noticia=noticia, avaliacao=5, comentario='Ruim', usuario=user1)

        user2 = User.objects.create_user(username='user_fb_2', password='pwd')
        perfilUsuario.objects.create(user=user2)
        Feedback.objects.create(tipo='noticia', noticia=noticia, avaliacao=7, comentario='Médio', usuario=user2)

        user3 = User.objects.create_user(username='user_fb_3', password='pwd')
        perfilUsuario.objects.create(user=user3)
        Feedback.objects.create(tipo='noticia', noticia=noticia, avaliacao=10, comentario='Excelente', usuario=user3)

        self.login(username='journ_view_fb_h6', password='pass', create_user=False)
        
        self.browser.get(f'{self.live_server_url}/feedbacks/noticia/{noticia.id}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'titulo-noticia'))
        )
        
        page_source = self.browser.page_source
        
        self.assertIn('5/10', page_source)
        self.assertIn('7/10', page_source)
        self.assertIn('10/10', page_source)
        self.assertIn('Ruim', page_source)
        self.assertIn('Médio', page_source)
        self.assertIn('Excelente', page_source)
        self.assertIn('3 feedbacks', page_source)

    def test_feedback_noticia_nao_autenticado_nao_acessa_feedbacks(self):

        jornalista_user = User.objects.create_user(username='journ_acesso_fb', password='pass')
        jornalista = perfilJornalista.objects.create(user=jornalista_user)
        noticia = Noticia.objects.create(autor=jornalista, titulo='Noticia Acesso', conteudo='Conteudo')

        Feedback.objects.create(tipo='noticia', noticia=noticia, avaliacao=8, comentario='Bom')

        self.browser.delete_all_cookies()
        self.browser.get(f'{self.live_server_url}/feedbacks/noticia/{noticia.id}/')
        
        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/login')
        )
        
        self.assertIn('/login', self.browser.current_url)

