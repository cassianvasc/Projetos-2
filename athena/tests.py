from django.test import TestCase,LiveServerTestCase,override_settings
from Jornalista.models import Perfil as perfilJornalista
from .models import Perfil as perfilUsuario
from django.contrib.auth.models import User
from django.urls import reverse
from Jornalista.models import *
from .models import *
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
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

        futebolButton = self.browser.find_element(By.CSS_SELECTOR,f'input[type="checkbox"][value="{ futebolTag.id }"]')
        politicaButton = self.browser.find_element(By.CSS_SELECTOR,f'input[type="checkbox"][value="{ politicaTag.id }"]')
        saveButton = self.browser.find_element(By.NAME,"save")

        futebolButton.click()
        politicaButton.click()
        saveButton.click()

        self.browser.get(f'{self.live_server_url}/')

        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.NAME,'user'))
        )

        button = self.browser.find_element(By.NAME,"user")
        button.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/user/')
        )

        futebolButton = self.browser.find_element(By.CSS_SELECTOR,f'input[type="checkbox"][value="{ futebolTag.id }"]')
        saveButton = self.browser.find_element(By.NAME,"save")

        futebolButton.click()
        saveButton.click()

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

        noticia = self.browser.find_element(By.XPATH, f"//a[contains(@href, '/noticia/{self.noticia_a.id}')]")
        noticia.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/noticia/')
        )

        response_politica = self.client.get(
            reverse('noticias_por_tag', args=[self.tag_politica.slug])
        )

        tag = self.browser.find_element(By.XPATH,f"//a[contains(@href, '/tag/{self.tag_politica.slug}')]")
        tag.click()

        WebDriverWait(self.browser, 10).until(
            expected_conditions.url_contains('/tag/')
        )

        self.assertEqual(response_politica.status_code, 200)
        
        self.assertIn(self.noticia_a, response_politica.context['noticias'])
        self.assertIn(self.noticia_b, response_politica.context['noticias'])
        
        self.assertNotIn(self.noticia_c, response_politica.context['noticias'])

# Create your tests here.