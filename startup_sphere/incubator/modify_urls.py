import sys

with open('e:/Projects/GLS SEM-7 Django Project/Startup_Sphere/startup_sphere/incubator/urls.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "path('team/', views.team_list" in line:
        lines.insert(i+1, "    path('team/chat/', views.team_chat, name='team_chat'),\n    path('startups/<int:startup_id>/team/chat/', views.team_chat, name='team_chat_id'),\n")
        break
with open('e:/Projects/GLS SEM-7 Django Project/Startup_Sphere/startup_sphere/incubator/urls.py', 'w') as f:
    f.writelines(lines)
