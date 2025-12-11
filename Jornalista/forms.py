from django import forms
from .models import Noticia


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ["titulo", "resumo", "conteudo"]


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ["titulo", "resumo", "conteudo"]