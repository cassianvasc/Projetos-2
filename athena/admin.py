from django.contrib import admin
from .models import *

admin.site.register(Tag)
admin.site.register(Perfil)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('get_tipo', 'avaliacao', 'get_noticia', 'get_usuario', 'data_criacao')
    list_filter = ('tipo', 'avaliacao', 'data_criacao')
    search_fields = ('comentario', 'noticia__titulo', 'usuario__username')
    readonly_fields = ('data_criacao',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo', 'avaliacao', 'data_criacao')
        }),
        ('Conteúdo', {
            'fields': ('noticia', 'comentario')
        }),
        ('Usuário', {
            'fields': ('usuario',)
        }),
    )
    
    def get_tipo(self, obj):
        return obj.get_tipo_display()
    get_tipo.short_description = 'Tipo'
    
    def get_noticia(self, obj):
        return obj.noticia.titulo if obj.noticia else '—'
    get_noticia.short_description = 'Notícia'
    
    def get_usuario(self, obj):
        return obj.usuario.username if obj.usuario else 'Anônimo'
    get_usuario.short_description = 'Usuário'

# Register your models here.

