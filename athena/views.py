from django.shortcuts import render, get_object_or_404
from .models import Tag
from Jornalista.models import Noticia

from django.shortcuts import render,redirect

from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from .models import *

import random

def home_page(request):
    user = request.user
    noticias_recentes = Noticia.objects.order_by('-data_postagem')[:20]
    noticias = random.sample(list(noticias_recentes), min(5, len(noticias_recentes)))

    return render(request, "athena/home.html",{'usuario': user,'noticias':noticias})

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

def NoticiaPage(request,noticiaId):

    noticia = Noticia.objects.get(id=noticiaId)

    return render(request, 'athena/noticia.html',{'noticia': noticia})


def PesquisarPorNoticiaPage(request):
    termo = request.GET.get("BarraDePesquisa",'').strip()

    if not termo:
        return redirect('home')

    noticias_titulo = Noticia.objects.filter(titulo__icontains=termo)
    tagsRelacionadas = Tag.objects.filter(nome__icontains=termo)
    noticias_tags = Noticia.objects.filter(tags__in=tagsRelacionadas)

    noticias = (noticias_titulo | noticias_tags).distinct()

    return render(request, 'athena/pesquisa.html',{'noticias':noticias,'termo':termo})



def noticias_por_tag(request, tag_slug=None):

    if not Tag.objects.filter(slug=tag_slug).exists():
        return redirect('home')

    tag = Tag.objects.get(slug=tag_slug)

    noticias = Noticia.objects.filter(tags=tag).order_by('-data_postagem')
    
    context = {
        'tag': tag,
        'noticias': noticias
    }
    
    return render(request, 'athena/noticias_por_tag.html', context)



# Create your views here.
