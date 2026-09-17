import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

base = "templates/incubator/"
dbase = "templates/dashboard/"

# ----------------- INVESTORS -----------------

create_file(base + "investor_profile_form.html", """{% extends 'base.html' %}
{% block title %}Edit Investor Profile{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm">
                    <h4 class="fw-bold mb-4">Investor Profile</h4>
                    <form method="post">
                        {% csrf_token %}
                        <div class="row g-3">
                            {% for field in form %}
                            <div class="col-md-6">
                                <label class="form-label fw-medium">{{ field.label }}</label>
                                {{ field }}
                                {% if field.help_text %}<small class="form-text text-muted">{{ field.help_text }}</small>{% endif %}
                                {% if field.errors %}<div class="text-danger small mt-1">{{ field.errors }}</div>{% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Save Profile</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "investor_profile_detail.html", """{% extends 'base.html' %}
{% block title %}Investor Profile - {{ profile.user.get_full_name }}{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:investor_directory' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Directory
            </a>
        </div>
        <div class="card p-4 border-0 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3 class="fw-bold mb-1">{{ profile.user.get_full_name|default:profile.user.username }}</h3>
                    <p class="text-muted mb-0">{{ profile.organization_name|default:"Independent Investor" }} • <span class="badge bg-primary bg-opacity-10 text-primary">{{ profile.get_investor_type_display }}</span></p>
                </div>
                {% if request.user == profile.user %}
                <a href="{% url 'incubator:investor_profile_edit' %}" class="btn btn-outline-primary">Edit Profile</a>
                {% endif %}
            </div>
            
            <div class="row g-4">
                <div class="col-md-8">
                    <h6 class="fw-bold text-uppercase text-muted mb-2">Bio</h6>
                    <p>{{ profile.bio|default:"No bio provided." }}</p>
                    
                    <h6 class="fw-bold text-uppercase text-muted mt-4 mb-2">Investment Focus</h6>
                    <p>{{ profile.investment_focus|default:"Not specified." }}</p>
                    
                    <h6 class="fw-bold text-uppercase text-muted mt-4 mb-2">Preferred Industries</h6>
                    <p>{{ profile.preferred_industries|default:"Not specified." }}</p>
                    
                    <h6 class="fw-bold text-uppercase text-muted mt-4 mb-2">Preferred Startup Stages</h6>
                    <p>{{ profile.preferred_startup_stages|default:"Not specified." }}</p>
                </div>
                <div class="col-md-4">
                    <div class="bg-light p-3 rounded">
                        <h6 class="fw-bold mb-3">Details</h6>
                        <ul class="list-unstyled mb-0">
                            <li class="mb-2"><i class="bi bi-geo-alt me-2 text-muted"></i> {{ profile.location|default:"Unknown" }}</li>
                            {% if profile.website %}
                            <li class="mb-2"><i class="bi bi-globe me-2 text-muted"></i> <a href="{{ profile.website }}" target="_blank">Website</a></li>
                            {% endif %}
                            {% if profile.linkedin_url %}
                            <li class="mb-2"><i class="bi bi-linkedin me-2 text-muted"></i> <a href="{{ profile.linkedin_url }}" target="_blank">LinkedIn</a></li>
                            {% endif %}
                            <li class="mb-2 mt-3 text-muted small text-uppercase">Investment Range</li>
                            <li class="fw-medium">${{ profile.min_investment|default:"0" }} - ${{ profile.max_investment|default:"Unlimited" }}</li>
                        </ul>
                        {% if request.user.role != 'investor' and request.user != profile.user %}
                        <a href="{% url 'incubator:collaboration_request_create' profile.user.id %}" class="btn btn-primary w-100 mt-4">Contact Investor</a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "investor_directory.html", """{% extends 'base.html' %}
{% block title %}Investor Directory{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Investor Directory</h4>
        </div>
        
        <div class="card p-3 mb-4 border-0 shadow-sm">
            <form method="get" class="row g-2 align-items-center">
                <div class="col-md-6">
                    <input type="text" name="q" class="form-control" placeholder="Search by name, org, or focus..." value="{{ query }}">
                </div>
                <div class="col-md-4">
                    <select name="investor_type" class="form-select">
                        <option value="">All Types</option>
                        <option value="angel" {% if investor_type == 'angel' %}selected{% endif %}>Angel Investor</option>
                        <option value="vc" {% if investor_type == 'vc' %}selected{% endif %}>Venture Capital</option>
                        <option value="corporate" {% if investor_type == 'corporate' %}selected{% endif %}>Corporate Investor</option>
                        <option value="seed" {% if investor_type == 'seed' %}selected{% endif %}>Seed Fund</option>
                        <option value="accelerator" {% if investor_type == 'accelerator' %}selected{% endif %}>Accelerator</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Search</button>
                </div>
            </form>
        </div>

        <div class="row g-4">
            {% for p in profiles %}
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm p-3 hover-shadow transition">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="fw-bold mb-0">{{ p.user.get_full_name|default:p.user.username }}</h6>
                        <span class="badge bg-primary bg-opacity-10 text-primary">{{ p.get_investor_type_display }}</span>
                    </div>
                    <p class="text-muted small mb-3">{{ p.organization_name|default:"Independent" }}</p>
                    <p class="small text-truncate mb-3">{{ p.investment_focus|default:"Focus not specified." }}</p>
                    <a href="{% url 'incubator:investor_profile_detail' p.user.id %}" class="btn btn-sm btn-outline-primary mt-auto">View Profile</a>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted mb-0">No investors found.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}""")

# ----------------- FUNDING ROUNDS -----------------

create_file(base + "funding_round_list.html", """{% extends 'base.html' %}
{% block title %}Funding Rounds{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">{% if is_founder %}My Funding Rounds{% else %}Funding Opportunities{% endif %}</h4>
            {% if is_founder %}
            <a href="{% url 'incubator:funding_round_create' %}" class="btn btn-primary fw-medium">Create Round</a>
            {% endif %}
        </div>
        
        <div class="row g-4">
            {% for r in rounds %}
            <div class="col-md-6 col-xl-4">
                <div class="card h-100 border-0 shadow-sm p-3 hover-shadow transition">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge bg-primary">{{ r.get_round_type_display }}</span>
                        {% if r.status == 'open' %}<span class="badge bg-success bg-opacity-10 text-success">Open</span>
                        {% elif r.status == 'closed' %}<span class="badge bg-danger bg-opacity-10 text-danger">Closed</span>
                        {% else %}<span class="badge bg-secondary bg-opacity-10 text-secondary">{{ r.get_status_display }}</span>{% endif %}
                    </div>
                    <h5 class="fw-bold mt-2 mb-1">{{ r.round_name }}</h5>
                    <p class="text-muted small mb-3">{{ r.startup.name }}</p>
                    <div class="d-flex justify-content-between small mb-3">
                        <div><span class="text-muted d-block">Target</span><span class="fw-bold">${{ r.target_amount }}</span></div>
                        <div class="text-end"><span class="text-muted d-block">Raised</span><span class="fw-bold">${{ r.raised_amount }}</span></div>
                    </div>
                    <a href="{% url 'incubator:funding_round_detail' r.id %}" class="btn btn-sm btn-outline-primary mt-auto">View Details</a>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted mb-0">No funding rounds available.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "funding_round_form.html", """{% extends 'base.html' %}
{% block title %}{{ title }}{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm">
                    <h4 class="fw-bold mb-4">{{ title }}</h4>
                    <form method="post">
                        {% csrf_token %}
                        <div class="row g-3">
                            {% for field in form %}
                            <div class="col-md-6">
                                <label class="form-label fw-medium">{{ field.label }}</label>
                                {{ field }}
                                {% if field.help_text %}<small class="form-text text-muted">{{ field.help_text }}</small>{% endif %}
                                {% if field.errors %}<div class="text-danger small mt-1">{{ field.errors }}</div>{% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4 d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Save Round</button>
                            <a href="{% url 'incubator:funding_round_list' %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "funding_round_detail.html", """{% extends 'base.html' %}
{% block title %}{{ round.round_name }}{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:funding_round_list' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Rounds
            </a>
        </div>
        
        <div class="row g-4">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <span class="badge bg-primary mb-2">{{ round.get_round_type_display }}</span>
                            <h3 class="fw-bold mb-1">{{ round.round_name }}</h3>
                            <p class="text-muted mb-0"><a href="{% url 'incubator:startup_detail' round.startup.id %}" class="text-decoration-none">{{ round.startup.name }}</a></p>
                        </div>
                        {% if is_owner %}
                        <a href="{% url 'incubator:funding_round_edit' round.id %}" class="btn btn-outline-primary">Edit Round</a>
                        {% endif %}
                        {% if request.user.role == 'investor' %}
                            {% if has_applied %}
                                <a href="{% url 'incubator:funding_application_detail' my_application.id %}" class="btn btn-success">View My Application</a>
                            {% elif round.status == 'open' %}
                                <a href="{% url 'incubator:funding_application_create' round.id %}" class="btn btn-primary">Apply to Invest</a>
                            {% endif %}
                        {% endif %}
                    </div>
                    
                    <div class="bg-light p-3 rounded mb-4">
                        <div class="row text-center">
                            <div class="col-4 border-end">
                                <span class="text-muted d-block small text-uppercase">Target</span>
                                <span class="fw-bold fs-5">${{ round.target_amount }}</span>
                            </div>
                            <div class="col-4 border-end">
                                <span class="text-muted d-block small text-uppercase">Raised</span>
                                <span class="fw-bold fs-5 text-success">${{ round.raised_amount }}</span>
                            </div>
                            <div class="col-4">
                                <span class="text-muted d-block small text-uppercase">Minimum</span>
                                <span class="fw-bold fs-5">${{ round.minimum_amount }}</span>
                            </div>
                        </div>
                    </div>
                    
                    <h6 class="fw-bold mb-2">Description</h6>
                    <p class="text-muted">{{ round.description|default:"No description provided." }}</p>
                </div>
                
                {% if is_owner or request.user.role == 'admin' %}
                <h5 class="fw-bold mb-3">Investor Applications</h5>
                <div class="card border-0 shadow-sm p-3">
                    <div class="table-responsive">
                        <table class="table align-middle">
                            <thead>
                                <tr>
                                    <th>Investor</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for app in applications %}
                                <tr>
                                    <td>{{ app.investor.username }}</td>
                                    <td class="fw-medium">${{ app.requested_amount }}</td>
                                    <td>
                                        {% if app.status == 'pending' %}<span class="badge bg-warning text-dark">Pending</span>
                                        {% elif app.status == 'accepted' %}<span class="badge bg-success">Accepted</span>
                                        {% elif app.status == 'rejected' %}<span class="badge bg-danger">Rejected</span>
                                        {% else %}<span class="badge bg-secondary">{{ app.get_status_display }}</span>{% endif %}
                                    </td>
                                    <td class="text-muted small">{{ app.created_at|date:"M d, Y" }}</td>
                                    <td><a href="{% url 'incubator:funding_application_detail' app.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="5" class="text-center text-muted py-3">No applications yet.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <div class="col-md-4">
                <div class="card p-3 border-0 shadow-sm mb-4">
                    <h6 class="fw-bold mb-3">Round Details</h6>
                    <ul class="list-unstyled mb-0">
                        <li class="mb-2"><span class="text-muted d-block small">Status</span><span class="fw-medium">{{ round.get_status_display }}</span></li>
                        <li class="mb-2"><span class="text-muted d-block small">Opening Date</span><span class="fw-medium">{{ round.opening_date|date:"M d, Y" }}</span></li>
                        <li class="mb-2"><span class="text-muted d-block small">Closing Date</span><span class="fw-medium">{{ round.closing_date|date:"M d, Y" }}</span></li>
                        {% if round.valuation %}
                        <li class="mb-2"><span class="text-muted d-block small">Valuation</span><span class="fw-medium">${{ round.valuation }}</span></li>
                        {% endif %}
                        {% if round.equity_offered %}
                        <li class="mb-2"><span class="text-muted d-block small">Equity Offered</span><span class="fw-medium">{{ round.equity_offered }}%</span></li>
                        {% endif %}
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

# ----------------- FUNDING APPLICATIONS -----------------

create_file(base + "funding_application_form.html", """{% extends 'base.html' %}
{% block title %}Apply for Funding{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm">
                    <h5 class="fw-bold mb-2">Apply for Funding</h5>
                    <p class="text-muted small mb-4">Round: {{ round.round_name }} • Startup: {{ round.startup.name }}</p>
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Requested Amount ($)</label>
                            {{ form.requested_amount }}
                            {% if form.requested_amount.errors %}<div class="text-danger small mt-1">{{ form.requested_amount.errors }}</div>{% endif %}
                            <div class="form-text">Minimum allowed for this round: ${{ round.minimum_amount }}</div>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-medium">Message to Founder</label>
                            {{ form.message }}
                            {% if form.message.errors %}<div class="text-danger small mt-1">{{ form.message.errors }}</div>{% endif %}
                        </div>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Submit Application</button>
                            <a href="{% url 'incubator:funding_round_detail' round.id %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "funding_application_list.html", """{% extends 'base.html' %}
{% block title %}Funding Applications{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Funding Applications</h4>
        </div>
        
        <div class="card border-0 shadow-sm p-3">
            <div class="table-responsive">
                <table class="table align-middle">
                    <thead>
                        <tr>
                            <th>Round</th>
                            <th>Startup</th>
                            <th>Investor</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for app in applications %}
                        <tr>
                            <td class="fw-medium">{{ app.funding_round.round_name }}</td>
                            <td>{{ app.funding_round.startup.name }}</td>
                            <td>{{ app.investor.username }}</td>
                            <td class="fw-medium">${{ app.requested_amount }}</td>
                            <td>
                                {% if app.status == 'pending' %}<span class="badge bg-warning text-dark">Pending</span>
                                {% elif app.status == 'accepted' %}<span class="badge bg-success">Accepted</span>
                                {% elif app.status == 'rejected' %}<span class="badge bg-danger">Rejected</span>
                                {% else %}<span class="badge bg-secondary">{{ app.get_status_display }}</span>{% endif %}
                            </td>
                            <td class="text-muted small">{{ app.created_at|date:"M d, Y" }}</td>
                            <td><a href="{% url 'incubator:funding_application_detail' app.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="7" class="text-center text-muted py-5">No applications found.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "funding_application_detail.html", """{% extends 'base.html' %}
{% block title %}Application Details{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:funding_application_list' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Applications
            </a>
        </div>
        
        <div class="row g-4">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h4 class="fw-bold mb-0">Application from {{ app.investor.username }}</h4>
                        <div>
                            {% if app.status == 'pending' %}<span class="badge bg-warning px-3 py-2 text-dark fs-6 rounded-pill">Pending</span>
                            {% elif app.status == 'accepted' %}<span class="badge bg-success px-3 py-2 fs-6 rounded-pill">Accepted</span>
                            {% elif app.status == 'rejected' %}<span class="badge bg-danger px-3 py-2 fs-6 rounded-pill">Rejected</span>
                            {% else %}<span class="badge bg-secondary px-3 py-2 fs-6 rounded-pill">{{ app.get_status_display }}</span>{% endif %}
                        </div>
                    </div>
                    
                    <div class="bg-light p-3 rounded mb-4">
                        <div class="row">
                            <div class="col-md-6 border-end">
                                <span class="text-muted d-block small">Funding Round</span>
                                <a href="{% url 'incubator:funding_round_detail' app.funding_round.id %}" class="fw-medium text-decoration-none">{{ app.funding_round.round_name }}</a>
                            </div>
                            <div class="col-md-6 text-end">
                                <span class="text-muted d-block small">Requested Amount</span>
                                <span class="fw-bold fs-5 text-primary">${{ app.requested_amount }}</span>
                            </div>
                        </div>
                    </div>
                    
                    <h6 class="fw-bold mb-2">Message</h6>
                    <div class="p-3 bg-light rounded text-muted mb-4" style="white-space: pre-wrap;">{{ app.message|default:"No message." }}</div>
                    
                    {% if is_owner and app.status == 'pending' or app.status == 'reviewing' %}
                    <div class="border-top pt-4">
                        <h6 class="fw-bold mb-3">Update Status</h6>
                        <form method="post" class="d-flex gap-2">
                            {% csrf_token %}
                            <button type="submit" name="status" value="reviewing" class="btn btn-outline-warning">Mark Reviewing</button>
                            <button type="submit" name="status" value="accepted" class="btn btn-success">Accept</button>
                            <button type="submit" name="status" value="rejected" class="btn btn-danger">Reject</button>
                        </form>
                    </div>
                    {% endif %}
                    
                    {% if is_investor and app.status == 'pending' %}
                    <div class="border-top pt-4">
                        <form action="{% url 'incubator:funding_application_withdraw' app.id %}" method="post">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-outline-danger" onclick="return confirm('Withdraw application?');">Withdraw Application</button>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card p-3 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-0">Meetings</h6>
                        {% if is_owner %}
                        <a href="{% url 'incubator:investor_meeting_create' app.id %}" class="btn btn-sm btn-primary">Schedule</a>
                        {% endif %}
                    </div>
                    
                    <ul class="list-group list-group-flush">
                        {% for meeting in meetings %}
                        <a href="{% url 'incubator:investor_meeting_detail' meeting.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                            <div class="d-flex justify-content-between">
                                <span class="fw-medium text-truncate">{{ meeting.scheduled_at|date:"M d, Y H:i" }}</span>
                                <span class="badge bg-secondary bg-opacity-10 text-secondary">{{ meeting.get_status_display }}</span>
                            </div>
                            <small class="text-muted">{{ meeting.get_meeting_type_display }} • {{ meeting.duration }}m</small>
                        </a>
                        {% empty %}
                        <li class="list-group-item px-0 text-muted small border-0">No meetings scheduled.</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

# ----------------- MEETINGS -----------------

create_file(base + "investor_meeting_form.html", """{% extends 'base.html' %}
{% block title %}Schedule Meeting{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm">
                    <h5 class="fw-bold mb-2">Schedule Meeting</h5>
                    <p class="text-muted small mb-4">With investor {{ app.investor.username }}</p>
                    <form method="post">
                        {% csrf_token %}
                        <div class="row g-3">
                            {% for field in form %}
                            <div class="col-md-12">
                                <label class="form-label fw-medium">{{ field.label }}</label>
                                {{ field }}
                                {% if field.errors %}<div class="text-danger small mt-1">{{ field.errors }}</div>{% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4 d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Schedule</button>
                            <a href="{% url 'incubator:funding_application_detail' app.id %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "investor_meeting_detail.html", """{% extends 'base.html' %}
{% block title %}Meeting Details{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:funding_application_detail' meeting.funding_application.id %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Application
            </a>
        </div>
        
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h4 class="fw-bold mb-0">Meeting Details</h4>
                        <div>
                            {% if meeting.status == 'scheduled' %}<span class="badge bg-primary px-3 py-2 rounded-pill">Scheduled</span>
                            {% elif meeting.status == 'completed' %}<span class="badge bg-success px-3 py-2 rounded-pill">Completed</span>
                            {% else %}<span class="badge bg-secondary px-3 py-2 rounded-pill">{{ meeting.get_status_display }}</span>{% endif %}
                        </div>
                    </div>
                    
                    <ul class="list-unstyled mb-4 border-bottom pb-4">
                        <li class="mb-2"><span class="text-muted d-inline-block" style="width: 120px;">Time</span><span class="fw-medium">{{ meeting.scheduled_at|date:"M d, Y H:i" }}</span></li>
                        <li class="mb-2"><span class="text-muted d-inline-block" style="width: 120px;">Duration</span><span class="fw-medium">{{ meeting.duration }} minutes</span></li>
                        <li class="mb-2"><span class="text-muted d-inline-block" style="width: 120px;">Type</span><span class="fw-medium">{{ meeting.get_meeting_type_display }}</span></li>
                        {% if meeting.meeting_link %}
                        <li class="mb-2"><span class="text-muted d-inline-block" style="width: 120px;">Link</span><a href="{{ meeting.meeting_link }}" target="_blank" class="fw-medium">Join Meeting <i class="bi bi-box-arrow-up-right ms-1"></i></a></li>
                        {% endif %}
                        {% if meeting.location %}
                        <li class="mb-2"><span class="text-muted d-inline-block" style="width: 120px;">Location</span><span class="fw-medium">{{ meeting.location }}</span></li>
                        {% endif %}
                    </ul>
                    
                    {% if meeting.agenda %}
                    <h6 class="fw-bold mb-2">Agenda</h6>
                    <p class="text-muted mb-4">{{ meeting.agenda }}</p>
                    {% endif %}
                    
                    {% if meeting.notes %}
                    <h6 class="fw-bold mb-2">Notes</h6>
                    <p class="text-muted mb-4">{{ meeting.notes }}</p>
                    {% endif %}
                    
                    {% if is_owner and meeting.status == 'scheduled' %}
                    <div class="d-flex gap-2 mt-2">
                        <form method="post">
                            {% csrf_token %}
                            <button type="submit" name="action" value="completed" class="btn btn-success">Mark Completed</button>
                            <button type="submit" name="action" value="cancelled" class="btn btn-outline-danger">Cancel Meeting</button>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

print("Templates script generated successfully.")
