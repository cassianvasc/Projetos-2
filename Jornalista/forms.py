from django import forms

from .models import Post

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["Título", "Conteúdo"]


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["Título", "Conteúdo"]