from django import forms
from .models import Perfil
from Jornalista.models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'resumo', 'conteudo', 'regiao', 'imagem', 'tags']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['tags', 'relevantes'] 
