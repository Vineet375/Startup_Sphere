from django.contrib import admin
from .models import Startup

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('name', 'founder', 'industry', 'stage', 'created_at')
    list_filter = ('industry', 'stage', 'created_at')
    search_fields = ('name', 'founder__username', 'founder__email', 'description')
