from django.urls import path
from . import views

app_name = 'incubator'

urlpatterns = [
    # Startup management
    path('startup/', views.startup_detail, name='startup_detail'),
    path('startup/<int:startup_id>/', views.startup_detail, name='startup_detail_id'),
    path('startup/register/', views.register_startup, name='register_startup'),
    path('startup/edit/', views.startup_edit, name='startup_edit'),
    
    # Idea management
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('ideas/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:idea_id>/edit/', views.idea_edit, name='idea_edit'),
    path('ideas/<int:idea_id>/submit/', views.idea_submit, name='idea_submit'),

    # Feedback
    path('ideas/<int:idea_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('ideas/<int:idea_id>/review/', views.mark_under_review, name='mark_under_review'),

    # Milestones (using startup_id or idea_id? milestone is tied to startup)
    path('startups/<int:startup_id>/milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:milestone_id>/edit/', views.milestone_update, name='milestone_update'),
    path('milestones/<int:milestone_id>/delete/', views.milestone_delete, name='milestone_delete'),
]
