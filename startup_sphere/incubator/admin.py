from django.contrib import admin
from .models import Startup, Idea, Feedback, Milestone

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('name', 'founder', 'mentor', 'category', 'stage', 'created_at')
    list_filter = ('category', 'stage', 'created_at')
    search_fields = ('name', 'founder__username', 'founder__email', 'tagline')

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'industry', 'created_at')
    list_filter = ('status', 'industry', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email', 'description')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('idea', 'mentor', 'created_at')
    search_fields = ('idea__title', 'mentor__username', 'content')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'startup', 'status', 'target_date')
    list_filter = ('status', 'target_date')
    search_fields = ('title', 'startup__name', 'description')
