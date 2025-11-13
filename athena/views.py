from django.shortcuts import render, get_object_or_404
from .models import Tag
from Jornalista.models import Noticia

from django.shortcuts import render,redirect

from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from .models import *

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from math import radians, cos, sin, asin, sqrt
import json
import random

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def home_page(request):
    user = request.user
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')

    noticias_recentes = Noticia.objects.order_by('-data_postagem')[:50]
    
    print(f"localização:{latitude},{longitude}")

    if latitude and longitude:
        noticias_proximas = [
            n for n in noticias_recentes
            if n.latitude and n.longitude and haversine(latitude, longitude, n.latitude, n.longitude) <= 50
        ]
        if noticias_proximas:
            noticias = random.sample(noticias_proximas, min(5, len(noticias_proximas)))
        else:
            noticias = random.sample(list(noticias_recentes), min(5, len(noticias_recentes)))
    else:
        noticias = random.sample(list(noticias_recentes), min(5, len(noticias_recentes)))
    
    context = {
        'usuario': user,
        'noticias': noticias,
        'logado': user.is_authenticated
    }
    return render(request, "athena/home.html", context)

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

    tag = get_object_or_404(Tag,slug=tag_slug)

    noticias = Noticia.objects.filter(tags=tag).order_by('-data_postagem')
    
    context = {
        'tag': tag,
        'noticias': noticias
    }
    
    return render(request, 'athena/noticias_por_tag.html', context)

@csrf_exempt  
def set_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Você pode salvar na sessão do usuário
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'fail'}, status=400)
# Create your views here.
