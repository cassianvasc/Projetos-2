from django.db import models
from django.contrib.auth.models import User 
from django.utils.text import slugify


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
    

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tags = models.ManyToManyField(Tag,blank=True,related_name='perfilComTag')
    relevantes = models.ManyToManyField('Jornalista.Noticia',blank=True,related_name='PerfilComNoticia')

    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)

    def __str__(self):
       return f"Perfil de {self.user.username}"


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Muito Ruim'),
        (2, '2 - Ruim'),
        (3, '3 - Razoável'),
        (4, '4 - Bom'),
        (5, '5 - Muito Bom'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10 - Excelente'),
    ]
    
    FEEDBACK_TYPE_CHOICES = [
        ('noticia', 'Feedback sobre Notícia'),
        ('site', 'Feedback sobre o Site'),
    ]
    
    # Identificação do feedback
    tipo = models.CharField(
        max_length=10,
        choices=FEEDBACK_TYPE_CHOICES,
        default='noticia',
        verbose_name='Tipo de Feedback'
    )
    
    # Relacionamento com notícia (opcional, apenas para feedbacks de notícia)
    noticia = models.ForeignKey(
        'Jornalista.Noticia',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name='Notícia'
    )
    
    # Avaliação
    avaliacao = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Avaliação (1-10)'
    )
    
    # Comentário
    comentario = models.TextField(
        max_length=500,
        verbose_name='Comentário',
        help_text='Deixe um comentário sobre o feedback (máximo 500 caracteres)'
    )
    
    # Usuário (opcional, pode ser anônimo)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meus_feedbacks',
        verbose_name='Usuário'
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-data_criacao']
    
    def __str__(self):
        if self.tipo == 'noticia':
            return f"Feedback na notícia '{self.noticia.titulo}' - {self.avaliacao}/10"
        else:
            return f"Feedback no Site - {self.avaliacao}/10"