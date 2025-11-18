from django import forms
from Jornalista.models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'conteudo', 'regiao', 'imagem', 'tags']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

