import os

event_list_html = """{% extends 'base.html' %}
{% block title %}Events & Workshops | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h4 class="fw-bold mb-1">Events & Workshops</h4>
                <p class="text-muted small">Discover and register for ecosystem events.</p>
            </div>
            {% if request.user.role == 'admin' or request.user.role == 'mentor' %}
            <a href="{% url 'incubator:event_create' %}" class="btn btn-primary fw-medium"><i class="bi bi-plus-lg me-1"></i> Create Event</a>
            {% endif %}
        </div>
        
        <div class="card p-3 mb-4 border-0 shadow-sm bg-light">
            <form method="get" class="row g-2 align-items-center">
                <div class="col-md-6">
                    <input type="text" name="q" class="form-control" placeholder="Search events..." value="{{ query }}">
                </div>
                <div class="col-md-4">
                    <select name="status" class="form-select">
                        <option value="upcoming" {% if status_filter == 'upcoming' %}selected{% endif %}>Upcoming</option>
                        <option value="ongoing" {% if status_filter == 'ongoing' %}selected{% endif %}>Ongoing</option>
                        <option value="completed" {% if status_filter == 'completed' %}selected{% endif %}>Completed</option>
                        <option value="" {% if not status_filter %}selected{% endif %}>All Statuses</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Filter</button>
                </div>
            </form>
        </div>

        <div class="row g-4">
            {% for event in events %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 border hover-shadow transition">
                    <div class="card-body">
                        <div class="d-flex justify-content-between mb-2">
                            <span class="badge bg-primary bg-opacity-10 text-primary">{{ event.get_event_type_display }}</span>
                            {% if event.status == 'upcoming' %}
                            <span class="badge bg-success bg-opacity-10 text-success">Upcoming</span>
                            {% elif event.status == 'cancelled' %}
                            <span class="badge bg-danger bg-opacity-10 text-danger">Cancelled</span>
                            {% else %}
                            <span class="badge bg-secondary bg-opacity-10 text-secondary">{{ event.get_status_display }}</span>
                            {% endif %}
                        </div>
                        <h5 class="fw-bold mb-2">{{ event.title }}</h5>
                        <p class="text-muted small mb-3 text-truncate">{{ event.description }}</p>
                        
                        <div class="mb-2 small text-muted">
                            <i class="bi bi-calendar-event me-2 text-primary"></i>{{ event.start_datetime|date:"M d, Y" }}
                        </div>
                        <div class="mb-2 small text-muted">
                            <i class="bi bi-clock me-2 text-primary"></i>{{ event.start_datetime|date:"H:i" }} - {{ event.end_datetime|date:"H:i" }}
                        </div>
                        {% if event.venue %}
                        <div class="mb-3 small text-muted text-truncate">
                            <i class="bi bi-geo-alt me-2 text-primary"></i>{{ event.venue }}
                        </div>
                        {% else %}
                        <div class="mb-3 small text-muted">
                            <i class="bi bi-camera-video me-2 text-primary"></i>Online Event
                        </div>
                        {% endif %}
                    </div>
                    <div class="card-footer bg-white border-top d-flex justify-content-between align-items-center">
                        {% if event.id in registered_event_ids %}
                        <span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Registered</span>
                        {% else %}
                        <span class="text-muted small">
                            {% if event.capacity %}{{ event.participations.count }} / {{ event.capacity }} slots{% else %}Unlimited slots{% endif %}
                        </span>
                        {% endif %}
                        <a href="{% url 'incubator:event_detail' event.id %}" class="btn btn-sm btn-outline-primary">Details</a>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-12">
                <div class="text-center py-5 card border-0 shadow-sm">
                    <div class="text-muted mb-3"><i class="bi bi-calendar-x fs-1"></i></div>
                    <h5 class="fw-bold">No Events Found</h5>
                    <p class="text-muted mb-0">There are no events matching your search criteria.</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/event_list.html', 'w', encoding='utf-8') as f: f.write(event_list_html)

event_detail_html = """{% extends 'base.html' %}
{% block title %}{{ event.title }} | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:event_list' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Events
            </a>
        </div>
        
        <div class="row g-4">
            <div class="col-lg-8">
                <div class="card p-4 shadow-sm border-0 mb-4">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <span class="badge bg-primary px-3 py-2 rounded-pill">{{ event.get_event_type_display }}</span>
                        {% if request.user.role == 'admin' or request.user == event.organizer %}
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="dropdown"><i class="bi bi-three-dots-vertical"></i></button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="{% url 'incubator:event_edit' event.id %}"><i class="bi bi-pencil me-2"></i>Edit Event</a></li>
                                <li><a class="dropdown-item" href="{% url 'incubator:event_participants' event.id %}"><i class="bi bi-people me-2"></i>Manage Participants</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <form action="{% url 'incubator:event_cancel' event.id %}" method="post">
                                        {% csrf_token %}
                                        <button type="submit" class="dropdown-item text-danger" onclick="return confirm('Are you sure you want to cancel this event?');"><i class="bi bi-x-circle me-2"></i>Cancel Event</button>
                                    </form>
                                </li>
                            </ul>
                        </div>
                        {% endif %}
                    </div>
                    
                    <h2 class="fw-bold mb-3">{{ event.title }}</h2>
                    <p class="text-muted fs-6 mb-4">{{ event.description|linebreaks }}</p>
                    
                    <h6 class="fw-bold mb-3">Event Details</h6>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <div class="d-flex">
                                <div class="bg-primary bg-opacity-10 text-primary rounded p-2 me-3"><i class="bi bi-calendar-event fs-5"></i></div>
                                <div>
                                    <small class="text-muted d-block">Date & Time</small>
                                    <strong>{{ event.start_datetime|date:"M d, Y H:i" }}</strong><br>
                                    <small class="text-muted">to {{ event.end_datetime|date:"M d, Y H:i" }}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex">
                                <div class="bg-success bg-opacity-10 text-success rounded p-2 me-3"><i class="bi bi-geo-alt fs-5"></i></div>
                                <div>
                                    <small class="text-muted d-block">Location</small>
                                    <strong>{{ event.venue|default:"Online Event" }}</strong>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex">
                                <div class="bg-info bg-opacity-10 text-info rounded p-2 me-3"><i class="bi bi-person fs-5"></i></div>
                                <div>
                                    <small class="text-muted d-block">Organizer</small>
                                    <strong>{{ event.organizer.get_full_name|default:event.organizer.username }}</strong>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex">
                                <div class="bg-warning bg-opacity-10 text-warning rounded p-2 me-3"><i class="bi bi-people fs-5"></i></div>
                                <div>
                                    <small class="text-muted d-block">Capacity</small>
                                    <strong>{% if event.capacity %}{{ current_participants }} / {{ event.capacity }} Registered{% else %}Unlimited{% endif %}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {% if event.meeting_link and participation.status == 'registered' and event.status != 'cancelled' %}
                    <div class="alert alert-info d-flex align-items-center mt-3">
                        <i class="bi bi-link-45deg fs-4 me-3"></i>
                        <div>
                            <strong>Meeting Link:</strong> <a href="{{ event.meeting_link }}" target="_blank" class="alert-link">{{ event.meeting_link }}</a>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card p-4 shadow-sm border-0 sticky-top" style="top: 20px;">
                    <h5 class="fw-bold mb-4">Registration</h5>
                    
                    {% if event.status == 'cancelled' %}
                    <div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i>This event has been cancelled.</div>
                    {% elif event.status == 'completed' %}
                    <div class="alert alert-secondary text-center"><i class="bi bi-info-circle me-2"></i>This event has already ended.</div>
                    {% elif event.status == 'ongoing' %}
                    <div class="alert alert-warning text-center"><i class="bi bi-clock-history me-2"></i>This event is currently ongoing.</div>
                    {% else %}
                        {% if request.user.is_authenticated %}
                            {% if participation and participation.status == 'registered' %}
                                <div class="text-center mb-4">
                                    <div class="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                                        <i class="bi bi-check-lg fs-2"></i>
                                    </div>
                                    <h5 class="fw-bold text-success">You're Registered!</h5>
                                    <p class="text-muted small">Registered on {{ participation.registered_at|date:"M d, Y" }}</p>
                                </div>
                                <form action="{% url 'incubator:event_unregister' event.id %}" method="post">
                                    {% csrf_token %}
                                    <button type="submit" class="btn btn-outline-danger w-100" onclick="return confirm('Are you sure you want to cancel your registration?');">Cancel Registration</button>
                                </form>
                            {% else %}
                                {% if is_full %}
                                <div class="alert alert-warning text-center"><i class="bi bi-exclamation-circle me-2"></i>This event is currently full.</div>
                                {% else %}
                                <form action="{% url 'incubator:event_register' event.id %}" method="post">
                                    {% csrf_token %}
                                    <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Register Now</button>
                                </form>
                                {% endif %}
                            {% endif %}
                        {% else %}
                            <div class="alert alert-info text-center">Please log in to register for this event.</div>
                            <a href="{% url 'accounts:login' %}?next={{ request.path }}" class="btn btn-primary w-100">Log In</a>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/event_detail.html', 'w', encoding='utf-8') as f: f.write(event_detail_html)

event_form_html = """{% extends 'base.html' %}
{% block title %}{{ title }} | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 shadow-sm border-0">
                    <h4 class="fw-bold mb-4">{{ title }}</h4>
                    <form method="post">
                        {% csrf_token %}
                        {% if form.non_field_errors %}
                        <div class="alert alert-danger">{{ form.non_field_errors }}</div>
                        {% endif %}
                        
                        <div class="mb-3">
                            <label class="form-label fw-medium">Event Title</label>
                            {{ form.title }}
                            <div class="text-danger small mt-1">{{ form.title.errors }}</div>
                        </div>
                        
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label fw-medium">Event Type</label>
                                {{ form.event_type }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-medium">Capacity (Optional)</label>
                                {{ form.capacity }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-medium">Description</label>
                            {{ form.description }}
                        </div>
                        
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label fw-medium">Start Date & Time</label>
                                {{ form.start_datetime }}
                                <div class="text-danger small mt-1">{{ form.start_datetime.errors }}</div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-medium">End Date & Time</label>
                                {{ form.end_datetime }}
                                <div class="text-danger small mt-1">{{ form.end_datetime.errors }}</div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-medium">Venue (Leave blank if online)</label>
                            {{ form.venue }}
                        </div>
                        
                        <div class="mb-4">
                            <label class="form-label fw-medium">Meeting Link (Optional)</label>
                            {{ form.meeting_link }}
                        </div>
                        
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Save Event</button>
                            <a href="{% url 'incubator:event_list' %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/event_form.html', 'w', encoding='utf-8') as f: f.write(event_form_html)

event_participants_html = """{% extends 'base.html' %}
{% block title %}Manage Participants - {{ event.title }} | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:event_detail' event.id %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Event Details
            </a>
        </div>
        <h4 class="fw-bold mb-4">Participants: {{ event.title }}</h4>
        
        <div class="card p-0 overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">User</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Registered At</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in participants %}
                        <tr>
                            <td class="ps-4 fw-medium">{{ p.participant.get_full_name|default:p.participant.username }}</td>
                            <td><span class="badge bg-secondary">{{ p.participant.get_role_display }}</span></td>
                            <td>
                                {% if p.status == 'registered' %}
                                <span class="badge bg-primary bg-opacity-10 text-primary">Registered</span>
                                {% elif p.status == 'attended' %}
                                <span class="badge bg-success bg-opacity-10 text-success">Attended</span>
                                {% else %}
                                <span class="badge bg-danger bg-opacity-10 text-danger">Cancelled</span>
                                {% endif %}
                            </td>
                            <td class="text-muted small">{{ p.registered_at|date:"M d, Y H:i" }}</td>
                            <td>
                                {% if p.status == 'registered' %}
                                <form action="{% url 'incubator:event_mark_attendance' event.id p.id %}" method="post" class="m-0">
                                    {% csrf_token %}
                                    <button type="submit" class="btn btn-sm btn-success">Mark Attended</button>
                                </form>
                                {% elif p.status == 'attended' %}
                                <span class="text-muted small">Attended at {{ p.attended_at|date:"H:i" }}</span>
                                {% else %}
                                -
                                {% endif %}
                            </td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="5" class="text-center py-4 text-muted">No participants found.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""
with open('templates/incubator/event_participants.html', 'w', encoding='utf-8') as f: f.write(event_participants_html)
