from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import LivePodcast

# Create your views here.

def podcast_player(request, podcast_id):
    podcast = get_object_or_404(LivePodcast, id=podcast_id)
    context = {
        'podcast': podcast,
    }
   
    return render(request, 'podcast/player.html', context)

def live_podcasts_list(request):
    podcasts = LivePodcast.objects.filter(is_live=True)
  
    return render(request, 'podcast/list.html', {'podcasts': podcasts})

@require_http_methods(["GET"])
def podcast_status(request, podcast_id):
    podcast = get_object_or_404(LivePodcast, id=podcast_id)
    return JsonResponse({
        'id': podcast.id,
        'title': podcast.title,
        'is_live': podcast.is_live,
        'stream_url': podcast.stream_url,
    })