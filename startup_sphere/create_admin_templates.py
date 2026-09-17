import os

os.makedirs('templates/dashboard', exist_ok=True)
os.makedirs('templates/incubator', exist_ok=True)

admin_dashboard_html = """{% extends 'base.html' %}
{% block title %}Admin Dashboard | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Platform Admin Dashboard</h4>
        
        <div class="row g-4 mb-4">
            <div class="col-md-3">
                <div class="card p-3 h-100 shadow-sm border-0 bg-primary text-white">
                    <h6 class="fw-bold mb-2">Users</h6>
                    <h2 class="mb-0">{{ total_users }}</h2>
                    <small>{{ founders_count }} Founders | {{ mentors_count }} Mentors</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card p-3 h-100 shadow-sm border-0 bg-success text-white">
                    <h6 class="fw-bold mb-2">Startups</h6>
                    <h2 class="mb-0">{{ total_startups }}</h2>
                    <small>{{ active_startups }} Active/Graduated</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card p-3 h-100 shadow-sm border-0 bg-warning text-dark">
                    <h6 class="fw-bold mb-2">Ideas</h6>
                    <h2 class="mb-0">{{ total_ideas }}</h2>
                    <small>{{ pending_ideas }} Pending Review</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card p-3 h-100 shadow-sm border-0 bg-info text-dark">
                    <h6 class="fw-bold mb-2">Events</h6>
                    <h2 class="mb-0">{{ total_events }}</h2>
                    <small>{{ upcoming_events }} Upcoming</small>
                </div>
            </div>
        </div>
        
        <div class="row g-4 mb-4">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm h-100">
                    <h6 class="fw-bold mb-3">Recent Startups</h6>
                    <div class="list-group list-group-flush">
                        {% for s in recent_startups %}
                        <a href="{% url 'incubator:startup_detail_id' s.id %}" class="list-group-item list-group-item-action px-0">
                            <strong>{{ s.name }}</strong> <span class="badge bg-secondary float-end">{{ s.get_incubation_status_display }}</span>
                        </a>
                        {% empty %}
                        <p class="text-muted small">No startups registered yet.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm h-100">
                    <h6 class="fw-bold mb-3">Other KPIs</h6>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            Total Collaborations
                            <span class="badge bg-primary rounded-pill">{{ total_collabs }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            Pending Collaborations
                            <span class="badge bg-warning rounded-pill">{{ pending_collabs }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            Total Evaluations
                            <span class="badge bg-success rounded-pill">{{ total_evals }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            Total Documents
                            <span class="badge bg-secondary rounded-pill">{{ total_docs }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock layout %}
"""
with open('templates/dashboard/admin_dashboard.html', 'w', encoding='utf-8') as f: f.write(admin_dashboard_html)

admin_users_html = """{% extends 'base.html' %}
{% block title %}Manage Users | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Manage Users</h4>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Joined</th>
                            <th>Active</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for u in users %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ u.username }}</td>
                            <td>{{ u.email }}</td>
                            <td><span class="badge bg-primary bg-opacity-10 text-primary">{{ u.get_role_display }}</span></td>
                            <td class="text-muted small">{{ u.date_joined|date:"M d, Y" }}</td>
                            <td>{% if u.is_active %}<span class="badge bg-success">Yes</span>{% else %}<span class="badge bg-danger">No</span>{% endif %}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_users.html', 'w', encoding='utf-8') as f: f.write(admin_users_html)

admin_startups_html = """{% extends 'base.html' %}
{% block title %}Manage Startups | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Manage Startups</h4>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Startup</th>
                            <th>Founder</th>
                            <th>Category</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for s in startups %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ s.name }}</td>
                            <td>{{ s.founder.username }}</td>
                            <td class="text-muted small">{{ s.category|default:"-" }}</td>
                            <td><span class="badge bg-secondary">{{ s.get_incubation_status_display }}</span></td>
                            <td class="text-muted small">{{ s.created_at|date:"M d, Y" }}</td>
                            <td><a href="{% url 'incubator:startup_detail_id' s.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_startups.html', 'w', encoding='utf-8') as f: f.write(admin_startups_html)

admin_ideas_html = """{% extends 'base.html' %}
{% block title %}Manage Ideas | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Manage Ideas</h4>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Title</th>
                            <th>Startup</th>
                            <th>Status</th>
                            <th>Submitted</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i in ideas %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ i.title }}</td>
                            <td>{{ i.startup.name }}</td>
                            <td><span class="badge bg-info">{{ i.get_status_display }}</span></td>
                            <td class="text-muted small">{{ i.submitted_at|date:"M d, Y"|default:"-" }}</td>
                            <td><a href="{% url 'incubator:idea_detail' i.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_ideas.html', 'w', encoding='utf-8') as f: f.write(admin_ideas_html)

admin_events_html = """{% extends 'base.html' %}
{% block title %}Manage Events | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Manage Events</h4>
            <a href="{% url 'incubator:event_create' %}" class="btn btn-primary">Create Event</a>
        </div>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Event</th>
                            <th>Type</th>
                            <th>Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for e in events %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ e.title }}</td>
                            <td>{{ e.get_event_type_display }}</td>
                            <td class="text-muted small">{{ e.start_datetime|date:"M d, Y H:i" }}</td>
                            <td><span class="badge bg-secondary">{{ e.get_status_display }}</span></td>
                            <td>
                                <a href="{% url 'incubator:event_detail' e.id %}" class="btn btn-sm btn-outline-primary">View</a>
                                <a href="{% url 'incubator:event_participants' e.id %}" class="btn btn-sm btn-outline-secondary">Participants</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_events.html', 'w', encoding='utf-8') as f: f.write(admin_events_html)

admin_collabs_html = """{% extends 'base.html' %}
{% block title %}Manage Collaborations | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Manage Collaborations</h4>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Type</th>
                            <th>Requester</th>
                            <th>Recipient</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for c in collabs %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ c.get_request_type_display }}</td>
                            <td>{{ c.requester.username }}</td>
                            <td>{{ c.recipient.username }}</td>
                            <td><span class="badge bg-secondary">{{ c.get_status_display }}</span></td>
                            <td class="text-muted small">{{ c.created_at|date:"M d, Y" }}</td>
                            <td><a href="{% url 'incubator:collaboration_detail' c.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_collabs.html', 'w', encoding='utf-8') as f: f.write(admin_collabs_html)

admin_activities_html = """{% extends 'base.html' %}
{% block title %}Audit Log | Admin{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <h4 class="fw-bold mb-4">Platform Audit Log</h4>
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Date</th>
                            <th>User</th>
                            <th>Startup</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for a in activities %}
                        <tr>
                            <td class="ps-4 text-muted small">{{ a.created_at|date:"M d, Y H:i" }}</td>
                            <td>{{ a.user.username|default:"System" }}</td>
                            <td>{{ a.startup.name }}</td>
                            <td><span class="badge bg-secondary">{{ a.get_activity_type_display }}</span></td>
                            <td class="small">{{ a.description }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/dashboard/admin_activities.html', 'w', encoding='utf-8') as f: f.write(admin_activities_html)
