import os

file_path = 'templates/core/landing.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_get_started = """<a href="{% url 'accounts:register' %}" class="btn btn-primary btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm d-flex align-items-center gap-2">
                        Get Started <i class="bi bi-arrow-right"></i>
                    </a>"""

new_get_started = """{% if request.user.is_authenticated %}
                    <a href="{% url 'dashboard:home' %}" class="btn btn-primary btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm d-flex align-items-center gap-2">
                        Get Started <i class="bi bi-arrow-right"></i>
                    </a>
                    {% else %}
                    <a href="{% url 'accounts:register' %}" class="btn btn-primary btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm d-flex align-items-center gap-2">
                        Get Started <i class="bi bi-arrow-right"></i>
                    </a>
                    {% endif %}"""

if old_get_started in content:
    content = content.replace(old_get_started, new_get_started)
else:
    print("Could not find old_get_started")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
