from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LivePodcast

@admin.register(LivePodcast)
class LivePodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_live', 'created_at', 'get_created_by']
    list_filter = ['is_live', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    
    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else 'Sistema'
    get_created_by.short_description = 'Criado por'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by:
             obj.created_by = request.user
        super().save_model(request, obj, form, change)