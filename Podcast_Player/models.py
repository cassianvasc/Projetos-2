from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class LivePodcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    stream_url = models.URLField(help_text="URL do stream (HLS, DASH, ou direct stream)")
    is_live = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='podcast_thumbnails/', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title