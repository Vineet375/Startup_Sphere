import os

file_path = 'dashboard/urls.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

admin_urls = """    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-startups/', views.admin_startups, name='admin_startups'),
    path('admin-ideas/', views.admin_ideas, name='admin_ideas'),
    path('admin-events/', views.admin_events, name='admin_events'),
    path('admin-collaborations/', views.admin_collaborations, name='admin_collaborations'),
    path('admin-activities/', views.admin_activities, name='admin_activities'),
]"""

content = content.replace("]", admin_urls)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
