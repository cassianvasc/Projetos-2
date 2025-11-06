from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Post
from .forms import PostCreateform, UpdatePostForm

# Create your views here.
@login_required
def editor_texto(request):
    if request.method == "POST":
        form = PostCreateform(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        
        else:
            form = PostCreateform()
        #Quando estiver com o frontend pronto coloca dentro do parâmetro do render!
        return render()
    
class atualizar_texto(request):
    model = Post
    form_class = UpdatePostForm
    template_name = ""
    success_message = "Matéria Atualizada!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False