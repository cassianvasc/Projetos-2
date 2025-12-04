from athena.models import *
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

class Perfil(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="perfil_jornalista")

    def __str__(self):
        return f"{self.user.username}"

class Noticia(models.Model):
    autor = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    resumo = models.CharField(max_length=200, blank=True, null=True, help_text="Resumo da notícia que aparecerá na home e pesquisas")
    conteudo = RichTextField()
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True)
    data_postagem = models.DateTimeField(auto_now_add=True)
    data_atualizada = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('athena.Tag', related_name='NoticiaComTag',blank=True)

    regiao = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["data_atualizada"]

    def save(self, *args, **kwargs):
        if self.regiao and (self.latitude is None or self.longitude is None):
            geolocator = Nominatim(user_agent="meu_app")
            location = geolocator.geocode(self.regiao)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
                print("tudo ok")
            else:
                print("localização não encontrada")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} {self.autor.user.username}"
    

