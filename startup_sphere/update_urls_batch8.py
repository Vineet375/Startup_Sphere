import os

file_path = 'incubator/urls.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_urls = """
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
]"""

content = content.replace("]", new_urls)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
