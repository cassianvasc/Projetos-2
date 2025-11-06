from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Perfil(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='perfil_jornalista')

    def __str__(self):
        return f"perfil de:{self.user.username}"

class Post(models.Model):
    jornalista = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    conteudo = RichTextField()
    data_postagem = models.DateTimeField(auto_now_add=True)
    data_atualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_atualizada"]


