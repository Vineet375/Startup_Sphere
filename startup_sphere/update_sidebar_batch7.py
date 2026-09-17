import os

file_path = 'templates/dashboard/_sidebar.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to add Events and Collaboration inside the sidebar for all users.
# And an Admin Section for admin users.

old_sidebar_links = """        <a href="{% url 'incubator:startup_directory' %}" class="nav-link mt-2 {% if 'directory' in request.resolver_match.url_name %}active{% endif %}">
            <i class="bi bi-globe"></i>
            Startup Directory
        </a>"""

new_sidebar_links = """        <a href="{% url 'incubator:startup_directory' %}" class="nav-link mt-2 {% if 'directory' in request.resolver_match.url_name %}active{% endif %}">
            <i class="bi bi-globe"></i>
            Startup Directory
        </a>
        
        <a href="{% url 'incubator:collaboration_directory' %}" class="nav-link {% if 'collaboration' in request.resolver_match.url_name %}active{% endif %}">
            <i class="bi bi-people-fill"></i>
            Collaboration
        </a>
        
        <a href="{% url 'incubator:event_list' %}" class="nav-link {% if 'event' in request.resolver_match.url_name %}active{% endif %}">
            <i class="bi bi-calendar-event"></i>
            Events & Workshops
        </a>
        
        {% if request.user.role == 'admin' %}
        <hr class="my-2 text-muted">
        <h6 class="sidebar-heading px-3 mt-2 mb-1 text-muted text-uppercase" style="font-size: 0.75rem;">Platform Admin</h6>
        
        <a href="{% url 'dashboard:admin_users' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_users' %}active{% endif %}">
            <i class="bi bi-person-badge"></i>
            Users
        </a>
        <a href="{% url 'dashboard:admin_startups' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_startups' %}active{% endif %}">
            <i class="bi bi-rocket"></i>
            Startups
        </a>
        <a href="{% url 'dashboard:admin_ideas' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_ideas' %}active{% endif %}">
            <i class="bi bi-lightbulb"></i>
            Ideas
        </a>
        <a href="{% url 'dashboard:admin_events' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_events' %}active{% endif %}">
            <i class="bi bi-calendar2-check"></i>
            Events Mgmt
        </a>
        <a href="{% url 'dashboard:admin_collaborations' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_collaborations' %}active{% endif %}">
            <i class="bi bi-diagram-3"></i>
            Collabs Mgmt
        </a>
        <a href="{% url 'dashboard:admin_activities' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_activities' %}active{% endif %}">
            <i class="bi bi-activity"></i>
            Audit Log
        </a>
        {% endif %}
"""

if old_sidebar_links in content:
    content = content.replace(old_sidebar_links, new_sidebar_links)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
