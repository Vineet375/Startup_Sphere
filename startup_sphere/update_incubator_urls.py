import os

file_path = 'incubator/urls.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_urls = """
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
]"""

content = content.replace("]", new_urls)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
