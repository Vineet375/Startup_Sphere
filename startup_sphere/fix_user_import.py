import os
file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I appended the new views at the end. Let's just do a replace for the imports.
if 'from core.models import User' not in content:
    content = content.replace("from django.db.models import Q", "from django.db.models import Q\nfrom core.models import User")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
