from django.contrib import admin
from .models import *

admin.site.register(Perfil)
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    fields = ('jornalista', 'titulo', 'conteudo', 'tags', 'regiao')
    
    exclude = ('latitude', 'longitude')
    
    list_display = ('titulo', 'jornalista', 'latitude', 'longitude')

# Register your models here.
