import os

file_path = 'templates/dashboard/_sidebar.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("{% url 'incubator:startup_detail' 0 %}", "{% url 'incubator:startup_detail' %}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
