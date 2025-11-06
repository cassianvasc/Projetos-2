from django.shortcuts import render, get_object_or_404
from .models import Noticia, Tag

from django.shortcuts import render,redirect

from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from .models import *

def home_page(request):

    user = request.user

    return render(request, "athena/home.html",{'usuario': user})

def loginPage(request):
    context = {}

    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=name,password=password)

        if user is not None:
            login(request, user)

            return redirect('home')
        else:
            context['error'] = "Nome de usuario ou senha incorreto"

    return render(request, "athena/login.html", context)

def registerPage(request):
    context = {}

    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not name or not email or not password:
            context['error'] = "preencha todos os campos"

            return render(request, "athena/register.html",context)
        elif User.objects.filter(username=name).exists():
            context['error'] = "um usuario com esse nome ja existe"

            return render(request, "athena/register.html",context)
    
        user = User.objects.create_user(username = name,email = email, password = password)
        Perfil.objects.create(user = user)

        return redirect('login')
    
    return render(request, "athena/register.html",context)

def UserAccountPage(request,usuario_id=None):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    perfil = user.perfil

    if usuario_id is None or usuario_id != user.id:
        return redirect('UserAccount',usuario_id=user.id)

    if request.method == 'POST':
        selectedTagsIds = request.POST.getlist('tags')
        selectedTags = Tag.objects.filter(id__in=selectedTagsIds)

        perfil.tags.set(selectedTags)

        return redirect('UserAccount',user.id)

    tags = Tag.objects.all()
    return render(request, "athena/UserAccount.html",{'usuario': user,'tags':tags})


def noticias_por_tag(request, tag_slug):
   
    tag = get_object_or_404(Tag, slug=tag_slug)
   
    noticias = Noticia.objects.filter(tags=tag).order_by('-data_publicacao')

   
    context = {
        'tag': tag,
        'noticias': noticias
    }
    
    return render(request, 'athena/noticias_por_tag.html', context)

# Create your views here.
