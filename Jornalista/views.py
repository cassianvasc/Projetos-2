from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from Podcast_Player.models import LivePodcast

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
    
def sua_view_da_home(request):
    podcasts_ao_vivo = LivePodcast.objects.filter(is_live=True).order_by('-created_at')[:5]
    contexto = {
    'usuario': request.user, 
    }
    contexto['live_podcasts'] = podcasts_ao_vivo
    
    return render(request, 'home.html', contexto)