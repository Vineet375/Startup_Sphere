from django.urls import path
from . import views

app_name = 'incubator'

urlpatterns = [
    # Startup management
    path('startup/', views.startup_detail, name='startup_detail'),
    path('startup/<int:startup_id>/', views.startup_detail, name='startup_detail_id'),
    path('startup/<int:startup_id>/status/', views.startup_update_status, name='startup_update_status'),
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

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),

    # Team Management
    path('team/', views.team_list, name='team_list'),
    path('startups/<int:startup_id>/team/', views.team_list, name='team_list_id'),
    path('team/invite/', views.team_invite, name='team_invite'),
    path('team/<int:member_id>/edit/', views.team_member_edit, name='team_member_edit'),
    path('team/<int:member_id>/remove/', views.team_remove, name='team_remove'),

    # Document Management
    path('documents/', views.document_list, name='document_list'),
    path('startups/<int:startup_id>/documents/', views.document_list, name='document_list_id'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:document_id>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
]
