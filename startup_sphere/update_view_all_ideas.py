import os

file_path = 'templates/incubator/startup_detail.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_view_all = """                                  {% if request.user == startup.founder %}
                                      <a href="{% url 'incubator:idea_list' %}" class="text-primary text-decoration-none small fw-medium">View All Ideas</a>
                                  {% else %}"""

new_view_all = """                                  {% if is_founder or is_team %}
                                      <a href="{% url 'incubator:idea_list' %}" class="text-primary text-decoration-none small fw-medium">View All Ideas</a>
                                  {% else %}"""

if old_view_all in content:
    content = content.replace(old_view_all, new_view_all)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
