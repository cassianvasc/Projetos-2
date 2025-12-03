from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Tag
from .forms import NoticiaForm
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.apps import apps
from django.core.paginator import Paginator

from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .models import *

from django.http import JsonResponse
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from math import radians, cos, sin, asin, sqrt
import json
import random

Noticia = apps.get_model('Jornalista', 'Noticia')
try:
    from Podcast_Player.models import LivePodcast
except Exception:
    LivePodcast = None

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

@require_POST
def FavoriteNews(request, noticiaId):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "not_authenticated"}, status=401)

    perfil = request.user.perfil
    noticia = get_object_or_404(Noticia, id=noticiaId)

    # toggle favorito
    if noticia in perfil.relevantes.all():
        perfil.relevantes.remove(noticia)
        return JsonResponse({"success": True, "favorited": False})
    else:
        perfil.relevantes.add(noticia)
        return JsonResponse({"success": True, "favorited": True})

def home_page(request):
    user = request.user
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')

    noticias_recentes = Noticia.objects.order_by('-data_postagem')[:50]
    favoritos = []
    favoritos_ids = []
    
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

    if user.is_authenticated:
        favoritos_ids = user.perfil.relevantes.values_list('id', flat=True)
        favoritos = Noticia.objects.filter(id__in=favoritos_ids)

        try:
            perfil_tags_qs = user.perfil.tags.all()
        except Exception:
            perfil_tags_qs = Tag.objects.none()

        if favoritos_ids:
            fav_tag_ids = Tag.objects.filter(NoticiaComTag__id__in=list(favoritos_ids)).values_list('id', flat=True)
        else:
            fav_tag_ids = []

        preferred_tag_ids = set(list(perfil_tags_qs.values_list('id', flat=True))) | set(list(fav_tag_ids))

        if preferred_tag_ids:
            noticias_by_tags = Noticia.objects.filter(tags__in=list(preferred_tag_ids)).distinct()
            lista_por_tag = list(noticias_by_tags)
            if lista_por_tag:
                noticias = random.sample(lista_por_tag, min(5, len(lista_por_tag)))

    live_podcast = None
    if LivePodcast is not None:
            live_podcast = LivePodcast.objects.filter(is_live=True).first()
    
    context = {
        'usuario': user,
        'noticias': noticias,
        'favoritos': favoritos,
        'favoritos_ids': favoritos_ids,
        'logado': user.is_authenticated,
        'jornalista': hasattr(user, "perfil_jornalista"),
        'live_podcast': live_podcast,
    }
    return render(request, "athena/home.html", context)

def loginPage(request):
    context = {}

    # accept next from GET (when redirecting to login) or POST (after form submit)
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        context['next'] = next_url

    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=name,password=password)

        if user is not None:
            login(request, user)
            # safe redirect to `next` if provided and allowed
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)
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

def UserAccountPage(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    perfil = user.perfil
    context = None

    if request.method == 'POST':
        selectedTagsIds = request.POST.getlist('tags')
        selectedTags = Tag.objects.filter(id__in=selectedTagsIds)

        perfil.tags.set(selectedTags)

        context = "Salvo com sucesso"

    tags = Tag.objects.all()
    return render(request, "athena/UserAccount.html",{'usuario': user,'tags':tags,'context':context})

def NoticiaPage(request,noticiaId):
    noticia = Noticia.objects.get(id=noticiaId)

    favoritos_ids = []
    if request.user.is_authenticated:
        try:
            favoritos_ids = request.user.perfil.relevantes.values_list('id', flat=True)
        except Exception:
            favoritos_ids = []

    context = {
        'noticia': noticia,
        'favoritos_ids': list(favoritos_ids),
        'logado': request.user.is_authenticated,
    }

    return render(request, 'athena/noticia.html', context)

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

    noticias = Noticia.objects.all().order_by('-data_postagem')

    if tag_slug != None:
        tag = get_object_or_404(Tag, slug=tag_slug)
        noticias = noticias.filter(tags=tag)
    else:
        tag = Tag(nome="Todas", slug="todas")

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

        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'fail'}, status=400)

def AddNoticiaPage(request):
    user = request.user

    if not hasattr(user, "perfil_jornalista"):
        return redirect("home")

    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES)  
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.autor = user.perfil_jornalista
            noticia.save()
            form.save_m2m()
            return redirect("home")
    else:
        form = NoticiaForm()

    return render(request, 'athena/addNoticia.html', {"form": form})

def load_more_news(request):
    page = int(request.GET.get("page", 1))

    exclude_param = request.GET.get('exclude', '')
    exclude_ids = []
    if exclude_param:
        try:
            exclude_ids = [int(x) for x in exclude_param.split(',') if x.strip().isdigit()]
        except Exception:
            exclude_ids = []

    noticias_recentes = Noticia.objects.exclude(id__in=exclude_ids).order_by("-data_postagem")

    paginator = Paginator(noticias_recentes, 5)

    try:
        noticias = paginator.page(page)
    except:
        return JsonResponse({"noticias": [], "has_next": False})

    data = []
    for n in noticias:
        # ensure excerpt is plain text (strip HTML) to avoid rendering raw tags
        plain = strip_tags(n.conteudo or "")
        excerpt = (plain[:150] + "...") if len(plain) > 150 else plain
        data.append({
            "id": n.id,
            "titulo": n.titulo,
            "excerpt": excerpt,
            "data": n.data_postagem.strftime("%d/%m/%Y"),
            "autor": str(n.autor) if n.autor else "",
            "tag": n.tag.nome if hasattr(n, "tag") else "",
            "imagem": n.imagem.url if n.imagem else None
        })

    return JsonResponse({
        "noticias": data,
        "has_next": noticias.has_next()
    })

def need_login(request):
    """Página simples informando que o usuário precisa entrar para favoritar.
    Recebe um parâmetro `next` na querystring para redirecionar depois do login.
    """
    next_url = request.GET.get('next', '/')
    return render(request, 'athena/need_login.html', {'next': next_url})
# Create your views here.
