from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
# Create your models here.

# NOVO MODELO: Tag
class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name='Nome da Tag')
    slug = models.SlugField(unique=True, max_length=60, blank=True)
    
  
    class Meta:
        verbose_name = 'Tag de Conteúdo'
        verbose_name_plural = 'Tags de Conteúdo'
    
   
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.nome

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    
    # Adicionar o campo aqui:
    tags = models.ManyToManyField(Tag, related_name='noticias')
    
    def __str__(self):
        return self.titulo
           
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    def __str__(self):
       return f"Perfil de {self.user.username}"
    
"""class Localização(models.Model):
    session_id = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.PointField(null=True, blank=True, srid=4326)
    city = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save_location(self, latitude, longitude, session_id, ip_address=None, user_agent=None):
        self.session_id = session_id
        self.ip_address = ip_address
        self.user_agent = user_agent or ''
        self.location = Point(longitude, latitude, srid=4326)
        self.save()
    def __str__(self):
        return f"Localização anônima: {self.session_id[:8]}..."""
