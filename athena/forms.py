from django import forms
from .models import Feedback
from Jornalista.models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'resumo', 'conteudo', 'regiao', 'imagem', 'tags']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['avaliacao', 'comentario']
        widgets = {
            'avaliacao': forms.RadioSelect(choices=Feedback.RATING_CHOICES),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deixe seu comentário aqui (máximo 500 caracteres)',
                'rows': 4,
                'maxlength': 500
            }),
        }
        labels = {
            'avaliacao': 'Como você avalia este conteúdo?',
            'comentario': 'Seu comentário',
        }


class FeedbackSiteForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['avaliacao', 'comentario']
        widgets = {
            'avaliacao': forms.RadioSelect(choices=Feedback.RATING_CHOICES),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deixe seu comentário sobre o site (máximo 500 caracteres)',
                'rows': 4,
                'maxlength': 500
            }),
        }
        labels = {
            'avaliacao': 'Como você avalia o site?',
            'comentario': 'Seu comentário',
        }

