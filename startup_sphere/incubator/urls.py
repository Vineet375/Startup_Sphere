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
    
    # Directory
    path('directory/', views.startup_directory, name='startup_directory'),
    path('directory/<int:startup_id>/', views.startup_public_profile, name='startup_public_profile'),
    
    # Evaluations
    path('startups/<int:startup_id>/evaluations/', views.evaluation_list, name='evaluation_list'),
    path('startups/<int:startup_id>/evaluations/create/', views.evaluation_create, name='evaluation_create'),
    path('evaluations/<int:evaluation_id>/edit/', views.evaluation_edit, name='evaluation_edit'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/cancel/', views.event_cancel, name='event_cancel'),
    path('events/<int:event_id>/register/', views.event_register, name='event_register'),
    path('events/<int:event_id>/unregister/', views.event_unregister, name='event_unregister'),
    path('events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
    path('events/<int:event_id>/participants/<int:participation_id>/attend/', views.event_mark_attendance, name='event_mark_attendance'),

    # Collaboration
    path('collaboration/directory/', views.collaboration_directory, name='collaboration_directory'),
    path('collaboration/request/<int:recipient_id>/', views.collaboration_request_create, name='collaboration_request_create'),
    path('collaboration/requests/', views.collaboration_list, name='collaboration_list'),
    path('collaboration/requests/<int:request_id>/', views.collaboration_detail, name='collaboration_detail'),
    path('collaboration/requests/<int:request_id>/accept/', views.collaboration_accept, name='collaboration_accept'),
    path('collaboration/requests/<int:request_id>/reject/', views.collaboration_reject, name='collaboration_reject'),
    path('collaboration/requests/<int:request_id>/cancel/', views.collaboration_cancel, name='collaboration_cancel'),

    # Investor Profiles
    path('investor/profile/', views.investor_profile_edit, name='investor_profile_edit'),
    path('investor/profile/<int:user_id>/', views.investor_profile_detail, name='investor_profile_detail'),
    path('investors/', views.investor_directory, name='investor_directory'),

    # Funding Rounds
    path('funding/', views.funding_round_list, name='funding_round_list'),
    path('funding/create/', views.funding_round_create, name='funding_round_create'),
    path('funding/<int:round_id>/', views.funding_round_detail, name='funding_round_detail'),
    path('funding/<int:round_id>/edit/', views.funding_round_edit, name='funding_round_edit'),
    
    # Funding Applications
    path('funding/<int:round_id>/apply/', views.funding_application_create, name='funding_application_create'),
    path('funding/applications/', views.funding_application_list, name='funding_application_list'),
    path('funding/applications/<int:app_id>/', views.funding_application_detail, name='funding_application_detail'),
    path('funding/applications/<int:app_id>/withdraw/', views.funding_application_withdraw, name='funding_application_withdraw'),
    
    # Investor Meetings
    path('funding/applications/<int:app_id>/meeting/', views.investor_meeting_create, name='investor_meeting_create'),
    path('meetings/<int:meeting_id>/', views.investor_meeting_detail, name='investor_meeting_detail'),

    # Jobs & Hiring
    path('jobs/', views.job_posting_list, name='job_posting_list'),
    path('jobs/directory/', views.job_directory, name='job_directory'),
    path('jobs/create/', views.job_posting_create, name='job_posting_create'),
    path('jobs/<int:job_id>/', views.job_posting_detail, name='job_posting_detail'),
    path('jobs/<int:job_id>/edit/', views.job_posting_edit, name='job_posting_edit'),
    
    # Job Applications
    path('jobs/<int:job_id>/apply/', views.job_application_create, name='job_application_create'),
    path('applications/', views.job_application_list, name='job_application_list'),
    path('applications/<int:app_id>/', views.job_application_detail, name='job_application_detail'),
    
    # Interviews
    path('applications/<int:app_id>/interview/', views.interview_create, name='interview_create'),
]
