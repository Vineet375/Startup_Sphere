import os

collab_dir_html = """{% extends 'base.html' %}
{% block title %}Collaboration Directory | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h4 class="fw-bold mb-1">Collaboration Directory</h4>
                <p class="text-muted small">Connect with founders, mentors, and investors.</p>
            </div>
            <a href="{% url 'incubator:collaboration_list' %}" class="btn btn-outline-primary fw-medium">My Requests</a>
        </div>
        
        <div class="card p-3 mb-4 border-0 shadow-sm">
            <form method="get" class="row g-2 align-items-center">
                <div class="col-md-10">
                    <input type="text" name="q" class="form-control" placeholder="Search by name or username..." value="{{ query }}">
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Search</button>
                </div>
            </form>
        </div>

        <div class="row g-4">
            {% for u in users %}
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="mb-3">
                        <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="bi bi-person-fill fs-3"></i>
                        </div>
                    </div>
                    <h6 class="fw-bold mb-1">{{ u.get_full_name|default:u.username }}</h6>
                    <p class="text-muted small mb-3"><span class="badge bg-secondary">{{ u.get_role_display }}</span></p>
                    <a href="{% url 'incubator:collaboration_request_create' u.id %}" class="btn btn-sm btn-outline-primary mt-auto">Request Collaboration</a>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted mb-0">No users found.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/collaboration_directory.html', 'w', encoding='utf-8') as f: f.write(collab_dir_html)

collab_form_html = """{% extends 'base.html' %}
{% block title %}Send Collaboration Request | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm">
                    <h5 class="fw-bold mb-3">Send Request to {{ recipient.username }}</h5>
                    <p class="text-muted small mb-4">They will be notified of your request and can choose to accept or decline.</p>
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Request Type</label>
                            {{ form.request_type }}
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Title</label>
                            {{ form.title }}
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-medium">Message</label>
                            {{ form.message }}
                            <div class="form-text">Explain why you want to collaborate and what you're looking for.</div>
                        </div>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Send Request</button>
                            <a href="{% url 'incubator:collaboration_directory' %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/collaboration_form.html', 'w', encoding='utf-8') as f: f.write(collab_form_html)

collab_list_html = """{% extends 'base.html' %}
{% block title %}My Collaboration Requests | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Collaboration Requests</h4>
            <a href="{% url 'incubator:collaboration_directory' %}" class="btn btn-primary fw-medium">Find Collaborators</a>
        </div>
        
        <ul class="nav nav-tabs mb-4" id="collabTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#received">Received Requests</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#sent">Sent Requests</button>
            </li>
        </ul>
        
        <div class="tab-content">
            <div class="tab-pane fade show active" id="received">
                <div class="row g-4">
                    {% for r in received_requests %}
                    <div class="col-md-6">
                        <div class="card p-3 border hover-shadow transition h-100">
                            <div class="d-flex justify-content-between mb-2">
                                <span class="badge bg-primary bg-opacity-10 text-primary">{{ r.get_request_type_display }}</span>
                                {% if r.status == 'pending' %}<span class="badge bg-warning bg-opacity-10 text-warning">Pending</span>
                                {% elif r.status == 'accepted' %}<span class="badge bg-success bg-opacity-10 text-success">Accepted</span>
                                {% elif r.status == 'rejected' %}<span class="badge bg-danger bg-opacity-10 text-danger">Rejected</span>
                                {% else %}<span class="badge bg-secondary bg-opacity-10 text-secondary">Cancelled</span>{% endif %}
                            </div>
                            <h6 class="fw-bold mb-1">{{ r.title }}</h6>
                            <p class="text-muted small mb-3">From: {{ r.requester.username }}</p>
                            <a href="{% url 'incubator:collaboration_detail' r.id %}" class="btn btn-sm btn-outline-primary mt-auto">View Details</a>
                        </div>
                    </div>
                    {% empty %}
                    <div class="col-12 text-center py-5">
                        <p class="text-muted mb-0">No received requests.</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="tab-pane fade" id="sent">
                <div class="row g-4">
                    {% for r in sent_requests %}
                    <div class="col-md-6">
                        <div class="card p-3 border hover-shadow transition h-100">
                            <div class="d-flex justify-content-between mb-2">
                                <span class="badge bg-primary bg-opacity-10 text-primary">{{ r.get_request_type_display }}</span>
                                {% if r.status == 'pending' %}<span class="badge bg-warning bg-opacity-10 text-warning">Pending</span>
                                {% elif r.status == 'accepted' %}<span class="badge bg-success bg-opacity-10 text-success">Accepted</span>
                                {% elif r.status == 'rejected' %}<span class="badge bg-danger bg-opacity-10 text-danger">Rejected</span>
                                {% else %}<span class="badge bg-secondary bg-opacity-10 text-secondary">Cancelled</span>{% endif %}
                            </div>
                            <h6 class="fw-bold mb-1">{{ r.title }}</h6>
                            <p class="text-muted small mb-3">To: {{ r.recipient.username }}</p>
                            <a href="{% url 'incubator:collaboration_detail' r.id %}" class="btn btn-sm btn-outline-secondary mt-auto">View Details</a>
                        </div>
                    </div>
                    {% empty %}
                    <div class="col-12 text-center py-5">
                        <p class="text-muted mb-0">No sent requests.</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/collaboration_list.html', 'w', encoding='utf-8') as f: f.write(collab_list_html)

collab_detail_html = """{% extends 'base.html' %}
{% block title %}Request Details | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:collaboration_list' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Requests
            </a>
        </div>
        
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <span class="badge bg-primary px-3 py-2 rounded-pill">{{ collab.get_request_type_display }}</span>
                        {% if collab.status == 'pending' %}<span class="badge bg-warning px-3 py-2 rounded-pill text-dark">Pending</span>
                        {% elif collab.status == 'accepted' %}<span class="badge bg-success px-3 py-2 rounded-pill">Accepted</span>
                        {% elif collab.status == 'rejected' %}<span class="badge bg-danger px-3 py-2 rounded-pill">Rejected</span>
                        {% else %}<span class="badge bg-secondary px-3 py-2 rounded-pill">Cancelled</span>{% endif %}
                    </div>
                    
                    <h4 class="fw-bold mb-2">{{ collab.title }}</h4>
                    <div class="text-muted small mb-4 border-bottom pb-3">
                        Requested by <strong>{{ collab.requester.username }}</strong> on {{ collab.created_at|date:"M d, Y" }}
                    </div>
                    
                    <h6 class="fw-bold mb-2">Message</h6>
                    <div class="bg-light p-3 rounded mb-4 text-muted" style="white-space: pre-wrap;">{{ collab.message }}</div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            {% if collab.responded_at %}
                            <small class="text-muted">Responded at {{ collab.responded_at|date:"M d, Y H:i" }}</small>
                            {% endif %}
                        </div>
                        
                        {% if collab.status == 'pending' %}
                            {% if request.user == collab.recipient %}
                            <div class="d-flex gap-2">
                                <form action="{% url 'incubator:collaboration_reject' collab.id %}" method="post" class="m-0">
                                    {% csrf_token %}<button type="submit" class="btn btn-outline-danger">Decline</button>
                                </form>
                                <form action="{% url 'incubator:collaboration_accept' collab.id %}" method="post" class="m-0">
                                    {% csrf_token %}<button type="submit" class="btn btn-success px-4">Accept Request</button>
                                </form>
                            </div>
                            {% elif request.user == collab.requester %}
                            <form action="{% url 'incubator:collaboration_cancel' collab.id %}" method="post" class="m-0">
                                {% csrf_token %}<button type="submit" class="btn btn-outline-secondary" onclick="return confirm('Cancel request?');">Cancel Request</button>
                            </form>
                            {% endif %}
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/collaboration_detail.html', 'w', encoding='utf-8') as f: f.write(collab_detail_html)
