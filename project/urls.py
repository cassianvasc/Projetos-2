"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from athena import views
from Podcast_Player import views as views_podcast

app_name = 'athena'

urlpatterns = [

    path('admin/', admin.site.urls),

    path('tag/<slug:tag_slug>/', views.noticias_por_tag, name='noticias_por_tag'),
    path('tag/', views.noticias_por_tag, name='noticias_por_tag'),
    
    path('pesquisa/', views.PesquisarPorNoticiaPage , name='pesquisa'),

    path('', views.home_page,name='home'),

    path('login/',views.loginPage,name='login'),

    path('register/',views.registerPage,name='register'),

    path('set-location/', views.set_location, name='set_location'), 

    path('noticia/<int:noticiaId>/', views.NoticiaPage, name='noticia'),

    path('user/',views.UserAccountPage,name='UserAccount'),

    path('player/<int:Podcast_id>/', views_podcast.podcast_player, name='player'),

    path('api/status/<int:Podcast_Player_id>/', views_podcast.podcast_status, name='status'),

    path('add/noticia', views.AddNoticiaPage , name="addNoticia"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
