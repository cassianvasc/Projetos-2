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

@override_settings(DEBUG=True)
class TesteE2E(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')        
        options.add_argument("--disable-infobars")
        options.add_argument("--incognito")

        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service,options=options)
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()


    def login(self):
        self.browser.delete_all_cookies()

        self.browser.get(f'{self.live_server_url}/login/')

        user = User.objects.create_user(username= 'teste', password='123')
        perfil = Perfil.objects.create(user=user)

        self.assertEqual(perfil.user.username,'teste')

        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.send_keys('teste')
        passwordInput.send_keys('123')
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

        self.assertTrue(User.objects.filter(username='teste').exists())

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'username'))
        )

        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

        usernameInput.send_keys('Erro')
        passwordInput.send_keys('Abc123!')
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser,10).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), "Nome de usuario ou senha incorreto")
        )

        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')

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
        time.sleep(1)
        self.assertEqual(user.perfil.tags.count(),1)


    def test_noticias_por_tag_slug_invalido(self):
        
        response = self.client.get(
            reverse('noticias_por_tag', args=['tag-que-nao-existe'])
        )

        self.assertEqual(response.status_code, 404)


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

        self.browser.get(f'{self.live_server_url}/')

        noticia = self.browser.find_element(
            By.XPATH,
            f"//a[@class='read-more-btn' and @href='/noticia/{self.noticia_a.id}/']"
        )
        actions = ActionChains(self.browser)
        actions.move_to_element(noticia).perform()
        noticia.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/noticia/')
        )

        response_politica = self.client.get(
            reverse('noticias_por_tag', args=[self.tag_politica.slug])
        )

        tag = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/tag/{self.tag_politica.slug}')]"))
        )

        self.browser.execute_script("arguments[0].click();", tag)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/tag/')
        )

        self.assertEqual(response_politica.status_code, 200)
        
        self.assertIn(self.noticia_a, response_politica.context['noticias'])
        self.assertIn(self.noticia_b, response_politica.context['noticias'])
        
        self.assertNotIn(self.noticia_c, response_politica.context['noticias'])

    def test_pesquisa_noticia(self):

        user = User.objects.create_user(username='jornalistaTeste')
        jornalista = perfilJornalista.objects.create(user=user)

        self.noticia_a = Noticia.objects.create(autor=jornalista,titulo='Título A', conteudo='Conteúdo A')

        self.browser.get(f'{self.live_server_url}/')

        search = self.browser.find_element(By.NAME,"BarraDePesquisa")
        searchButton = self.browser.find_element(By.CLASS_NAME,"search-btn")
        search.send_keys("Título A")
        searchButton.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/pesquisa/')
        )

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,f"{self.noticia_a.titulo}"))
        )

        self.browser.get(f'{self.live_server_url}/')

        search = self.browser.find_element(By.NAME,"BarraDePesquisa")
        searchButton = self.browser.find_element(By.CLASS_NAME,"search-btn")
        search.send_keys("nada")
        searchButton.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/pesquisa/')
        )

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,"context"))
        )

    def test_add_noticia_jornalista(self):
        # create a user and journalist profile, then login and add a noticia
        username = 'jornalista_add'
        password = 'Senha123!'
        user = User.objects.create_user(username=username, password=password)
        jornalista = perfilJornalista.objects.create(user=user)

        # go to login page and sign in
        self.browser.get(f'{self.live_server_url}/login/')
        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')
        usernameInput.send_keys(username)
        passwordInput.send_keys(password)
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        # click the "Adicionar Noticia" button/link in the header
        add_link = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Adicionar Noticia'))
        )
        add_link.click()

        # wait for addNoticia form to load (titulo field should be present)
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, 'titulo'))
        )

        # fill the form
        tituloInput = self.browser.find_element(By.NAME, 'titulo')
        regiaoInput = self.browser.find_element(By.NAME, 'regiao')
        conteudoInput = self.browser.find_element(By.NAME, 'conteudo')

        tituloInput.send_keys('Teste E2E - Nova Notícia')
        regiaoInput.send_keys('Recife')
        conteudoInput.send_keys('Conteúdo de teste para a nova notícia criada pelo E2E.')

        # submit the form
        submitBtn = self.browser.find_element(By.CSS_SELECTOR, 'button.botao-principal')
        submitBtn.click()

        # wait until redirected back to home (header user element visible)
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        # assert that noticia was created in the database
        from Jornalista.models import Noticia
        self.assertTrue(Noticia.objects.filter(titulo='Teste E2E - Nova Notícia').exists())

    def test_add_noticia_with_tags(self):
        # create a user and journalist profile, tags, then login and add a noticia with tags
        username = 'jornalista_tags'
        password = 'Senha123!'
        user = User.objects.create_user(username=username, password=password)
        jornalista = perfilJornalista.objects.create(user=user)

        # create tags before rendering form so they appear in select
        tag1 = Tag.objects.create(nome='Política')
        tag2 = Tag.objects.create(nome='Economia')

        # login
        self.browser.get(f'{self.live_server_url}/login/')
        usernameInput = self.browser.find_element(By.NAME,'username')
        passwordInput = self.browser.find_element(By.NAME,'password')
        usernameInput.send_keys(username)
        passwordInput.send_keys(password)
        passwordInput.send_keys(Keys.RETURN)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        # navigate to add noticia
        add_link = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Adicionar Noticia'))
        )
        add_link.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, 'titulo'))
        )

        # fill basic fields
        self.browser.find_element(By.NAME, 'titulo').send_keys('Teste Tags')
        self.browser.find_element(By.NAME, 'regiao').send_keys('Recife')

        # select tags using Select helper
        select_elem = Select(self.browser.find_element(By.NAME, 'tags'))
        # select by visible text (matches Tag.nome)
        select_elem.select_by_visible_text('Política')
        select_elem.select_by_visible_text('Economia')

        # fill content (if CKEditor present this may need JS injection; try textarea)
        conteudo = self.browser.find_element(By.NAME, 'conteudo')
        conteudo.send_keys('Conteúdo com tags para teste.')

        # submit
        self.browser.find_element(By.CSS_SELECTOR, 'button.botao-principal').click()

        # wait until redirected back to home
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        # verify noticia created and tags associated
        from Jornalista.models import Noticia
        noticia = Noticia.objects.filter(titulo='Teste Tags').first()
        self.assertIsNotNone(noticia)
        tag_names = set([t.nome for t in noticia.tags.all()])
        self.assertTrue('Política' in tag_names and 'Economia' in tag_names)

    def test_podcast_live_shows_on_home(self):
        
        if LivePodcast is None:
            self.skipTest('Podcast_Player app not available')

        lp = LivePodcast.objects.create(title='Ao Vivo - Teste', stream_url='https://example.com/stream.mp3', is_live=True)

        # visit home
        self.browser.get(f'{self.live_server_url}/')

        # wait for mini-player and check title and live badge
        mini = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'miniPodcast'))
        )

        title_el = self.browser.find_element(By.ID, 'miniPodcastTitle')
        self.assertIn('Ao Vivo - Teste', title_el.text)

        live_badge = self.browser.find_element(By.CLASS_NAME, 'live-badge')
        self.assertTrue(live_badge.is_displayed())

# Create your tests here.