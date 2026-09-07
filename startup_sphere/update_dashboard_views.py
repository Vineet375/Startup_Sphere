import os

file_path = 'dashboard/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure get_active_startup is imported
if 'get_active_startup' not in content:
    content = content.replace("from incubator.models import Startup, Idea", "from incubator.models import Startup, Idea\nfrom incubator.views import get_active_startup")

old_startup_check = """    if hasattr(request.user, 'startup'):
        startup = request.user.startup"""

new_startup_check = """    startup = get_active_startup(request.user)
    if startup:"""

if old_startup_check in content:
    content = content.replace(old_startup_check, new_startup_check)
else:
    print("Could not find old_startup_check in dashboard/views.py")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
