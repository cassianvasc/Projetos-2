from athena.models import *
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="perfil_jornalista")

    def __str__(self):
        return f"{self.user.username}"

class Noticia(models.Model):
    jornalista = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    conteudo = RichTextField()
    data_postagem = models.DateTimeField(auto_now_add=True)
    data_atualizada = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(Tag, related_name='NoticiaComTag',blank=True)

    class Meta:
        ordering = ["data_atualizada"]

    def __str__(self):
        return f"{self.titulo} {self.jornalista.user.username}"