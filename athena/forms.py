from django import forms
from Jornalista.models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'conteudo', 'regiao', 'tags']
