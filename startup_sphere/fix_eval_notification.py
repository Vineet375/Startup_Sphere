import os

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_link = "link_url=f'/startups/{startup.id}/evaluations/'"
new_link = "link_url=reverse('incubator:evaluation_list', args=[startup.id])"

if old_link in content:
    content = content.replace(old_link, new_link)
else:
    print("Not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
