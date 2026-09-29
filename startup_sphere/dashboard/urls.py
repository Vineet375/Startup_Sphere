from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('coming-soon/<str:feature>/', views.coming_soon_view, name='coming_soon'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-startups/', views.admin_startups, name='admin_startups'),
    path('admin-ideas/', views.admin_ideas, name='admin_ideas'),
    path('admin-events/', views.admin_events, name='admin_events'),
    path('admin-collaborations/', views.admin_collaborations, name='admin_collaborations'),
    path('admin-activities/', views.admin_activities, name='admin_activities'),
    path('search/', views.global_search, name='global_search'),
    path('settings/', views.settings_view, name='settings'),
]
