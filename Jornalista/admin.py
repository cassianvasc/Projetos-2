from django.contrib import admin
from .models import *

admin.site.register(Perfil)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    fields = ('autor', 'titulo', 'resumo', 'conteudo','imagem','tags', 'regiao')
    
    exclude = ('latitude', 'longitude')
    
# Register your models here.