from django.contrib import admin
from .models import Startup, Idea

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('name', 'founder', 'category', 'stage', 'created_at')
    list_filter = ('category', 'stage', 'created_at')
    search_fields = ('name', 'founder__username', 'founder__email', 'tagline')

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'industry', 'created_at')
    list_filter = ('status', 'industry', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email', 'description')
