import os

file_path = 'templates/incubator/startup_detail.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_update_btn = """                                        <div>
                                            <a href="{% url 'incubator:milestone_update' milestone.id %}" class="btn btn-sm btn-outline-secondary">Update</a>"""

new_update_btn = """                                        <div>
                                            {% if is_founder or is_mentor or is_admin %}
                                            <a href="{% url 'incubator:milestone_update' milestone.id %}" class="btn btn-sm btn-outline-secondary">Update</a>
                                            {% endif %}"""

if old_update_btn in content:
    content = content.replace(old_update_btn, new_update_btn)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
