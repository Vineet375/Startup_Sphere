import os

file_path = 'templates/base.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add a sidebar toggle button next to the brand on mobile
old_brand = """            <a class="navbar-brand d-flex align-items-center" href="{% url 'core:landing' %}">"""

new_brand = """            {% if request.user.is_authenticated %}
            <button class="navbar-toggler border-0 me-2 d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu">
                <i class="bi bi-layout-sidebar"></i>
            </button>
            {% endif %}
            <a class="navbar-brand d-flex align-items-center" href="{% url 'core:landing' %}">"""

if old_brand in content:
    content = content.replace(old_brand, new_brand)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
