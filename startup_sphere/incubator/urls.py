from django.urls import path
from . import views

app_name = 'incubator'

urlpatterns = [
    # Startup management
    path('startup/', views.startup_detail, name='startup_detail'),
    path('startup/register/', views.register_startup, name='register_startup'),
    path('startup/edit/', views.startup_edit, name='startup_edit'),
    
    # Idea management
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('ideas/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:idea_id>/edit/', views.idea_edit, name='idea_edit'),
    path('ideas/<int:idea_id>/submit/', views.idea_submit, name='idea_submit'),
]
