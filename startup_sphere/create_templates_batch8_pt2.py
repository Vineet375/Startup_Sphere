import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

base = "templates/incubator/"
dbase = "templates/dashboard/"

# ----------------- HIRING & JOBS -----------------

create_file(base + "job_posting_list.html", """{% extends 'base.html' %}
{% block title %}Job Postings{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">My Job Postings</h4>
            <a href="{% url 'incubator:job_posting_create' %}" class="btn btn-primary fw-medium">Create Job</a>
        </div>
        
        <div class="row g-4">
            {% for job in jobs %}
            <div class="col-md-6 col-xl-4">
                <div class="card h-100 border-0 shadow-sm p-3 hover-shadow transition">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge bg-primary bg-opacity-10 text-primary">{{ job.get_employment_type_display }}</span>
                        {% if job.status == 'published' %}<span class="badge bg-success bg-opacity-10 text-success">Published</span>
                        {% elif job.status == 'closed' %}<span class="badge bg-danger bg-opacity-10 text-danger">Closed</span>
                        {% else %}<span class="badge bg-secondary bg-opacity-10 text-secondary">{{ job.get_status_display }}</span>{% endif %}
                    </div>
                    <h5 class="fw-bold mt-2 mb-1">{{ job.title }}</h5>
                    <p class="text-muted small mb-3"><i class="bi bi-geo-alt me-1"></i> {{ job.location|default:"Remote" }}</p>
                    <a href="{% url 'incubator:job_posting_detail' job.id %}" class="btn btn-sm btn-outline-primary mt-auto">Manage Job</a>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted mb-0">No job postings created.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_directory.html", """{% extends 'base.html' %}
{% block title %}Job Directory{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Find Jobs</h4>
        </div>
        
        <div class="card p-3 mb-4 border-0 shadow-sm">
            <form method="get" class="row g-2 align-items-center">
                <div class="col-md-5">
                    <input type="text" name="q" class="form-control" placeholder="Search by title, description, or startup..." value="{{ query }}">
                </div>
                <div class="col-md-3">
                    <select name="employment_type" class="form-select">
                        <option value="">Any Employment Type</option>
                        <option value="full_time" {% if emp_type == 'full_time' %}selected{% endif %}>Full Time</option>
                        <option value="part_time" {% if emp_type == 'part_time' %}selected{% endif %}>Part Time</option>
                        <option value="internship" {% if emp_type == 'internship' %}selected{% endif %}>Internship</option>
                        <option value="contract" {% if emp_type == 'contract' %}selected{% endif %}>Contract</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <select name="experience_level" class="form-select">
                        <option value="">Any Level</option>
                        <option value="entry" {% if exp_level == 'entry' %}selected{% endif %}>Entry Level</option>
                        <option value="junior" {% if exp_level == 'junior' %}selected{% endif %}>Junior</option>
                        <option value="mid" {% if exp_level == 'mid' %}selected{% endif %}>Mid Level</option>
                        <option value="senior" {% if exp_level == 'senior' %}selected{% endif %}>Senior</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Search</button>
                </div>
            </form>
        </div>

        <div class="row g-4">
            {% for job in jobs %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 border-0 shadow-sm p-3 hover-shadow transition">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="fw-bold mb-0 text-truncate">{{ job.title }}</h6>
                        <span class="badge bg-primary bg-opacity-10 text-primary">{{ job.get_employment_type_display }}</span>
                    </div>
                    <p class="text-muted small mb-3">{{ job.startup.name }}</p>
                    <div class="d-flex gap-2 text-muted small mb-3">
                        <span><i class="bi bi-geo-alt me-1"></i> {% if job.is_remote %}Remote{% else %}{{ job.location }}{% endif %}</span>
                        <span><i class="bi bi-clock me-1"></i> {{ job.created_at|timesince }} ago</span>
                    </div>
                    <a href="{% url 'incubator:job_posting_detail' job.id %}" class="btn btn-sm btn-outline-primary mt-auto">View Details</a>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted mb-0">No jobs found.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_posting_form.html", """{% extends 'base.html' %}
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
                            <div class="col-md-{% if field.name == 'is_remote' %}12{% else %}6{% endif %}">
                                <label class="form-label fw-medium">{{ field.label }}</label>
                                {{ field }}
                                {% if field.help_text %}<small class="form-text text-muted">{{ field.help_text }}</small>{% endif %}
                                {% if field.errors %}<div class="text-danger small mt-1">{{ field.errors }}</div>{% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4 d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Save Job</button>
                            <a href="{% url 'incubator:job_posting_list' %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_posting_detail.html", """{% extends 'base.html' %}
{% block title %}{{ job.title }}{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% if is_owner %}{% url 'incubator:job_posting_list' %}{% else %}{% url 'incubator:job_directory' %}{% endif %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Jobs
            </a>
        </div>
        
        <div class="row g-4">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-start mb-4">
                        <div>
                            <span class="badge bg-primary mb-2">{{ job.get_employment_type_display }}</span>
                            <span class="badge bg-secondary mb-2 ms-1">{{ job.get_experience_level_display }}</span>
                            <h3 class="fw-bold mb-1">{{ job.title }}</h3>
                            <p class="text-muted mb-0"><a href="{% url 'incubator:startup_detail' job.startup.id %}" class="text-decoration-none">{{ job.startup.name }}</a></p>
                        </div>
                        {% if is_owner %}
                        <a href="{% url 'incubator:job_posting_edit' job.id %}" class="btn btn-outline-primary">Edit Job</a>
                        {% endif %}
                        {% if request.user.role == 'applicant' %}
                            {% if my_application %}
                                <a href="{% url 'incubator:job_application_detail' my_application.id %}" class="btn btn-success">View My Application</a>
                            {% elif job.status == 'published' %}
                                <a href="{% url 'incubator:job_application_create' job.id %}" class="btn btn-primary px-4">Apply Now</a>
                            {% endif %}
                        {% endif %}
                    </div>
                    
                    <h6 class="fw-bold text-uppercase text-muted mb-2">Description</h6>
                    <p class="mb-4" style="white-space: pre-wrap;">{{ job.description }}</p>
                    
                    <h6 class="fw-bold text-uppercase text-muted mb-2">Responsibilities</h6>
                    <p class="mb-4" style="white-space: pre-wrap;">{{ job.responsibilities }}</p>
                    
                    <h6 class="fw-bold text-uppercase text-muted mb-2">Requirements</h6>
                    <p class="mb-0" style="white-space: pre-wrap;">{{ job.requirements }}</p>
                </div>
                
                {% if is_owner or request.user.role == 'admin' %}
                <h5 class="fw-bold mb-3">Job Applications</h5>
                <div class="card border-0 shadow-sm p-3">
                    <div class="table-responsive">
                        <table class="table align-middle">
                            <thead>
                                <tr>
                                    <th>Applicant</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for app in applications %}
                                <tr>
                                    <td class="fw-medium">{{ app.applicant.get_full_name|default:app.applicant.username }}</td>
                                    <td class="text-muted small">{{ app.applied_at|date:"M d, Y" }}</td>
                                    <td>
                                        {% if app.status == 'submitted' %}<span class="badge bg-warning text-dark">Submitted</span>
                                        {% elif app.status == 'reviewing' %}<span class="badge bg-info">Reviewing</span>
                                        {% elif app.status == 'shortlisted' %}<span class="badge bg-primary">Shortlisted</span>
                                        {% elif app.status == 'interview' %}<span class="badge bg-primary">Interview</span>
                                        {% elif app.status == 'rejected' %}<span class="badge bg-danger">Rejected</span>
                                        {% elif app.status == 'hired' %}<span class="badge bg-success">Hired</span>
                                        {% else %}<span class="badge bg-secondary">{{ app.get_status_display }}</span>{% endif %}
                                    </td>
                                    <td><a href="{% url 'incubator:job_application_detail' app.id %}" class="btn btn-sm btn-outline-primary">Review</a></td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="4" class="text-center text-muted py-3">No applications yet.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <div class="col-md-4">
                <div class="card p-3 border-0 shadow-sm mb-4">
                    <h6 class="fw-bold mb-3">Job Details</h6>
                    <ul class="list-unstyled mb-0">
                        <li class="mb-2"><span class="text-muted d-block small">Status</span><span class="fw-medium">{{ job.get_status_display }}</span></li>
                        <li class="mb-2"><span class="text-muted d-block small">Location</span><span class="fw-medium">{% if job.is_remote %}Remote{% else %}{{ job.location|default:"Not specified" }}{% endif %}</span></li>
                        {% if job.salary_min or job.salary_max %}
                        <li class="mb-2"><span class="text-muted d-block small">Salary</span><span class="fw-medium">${{ job.salary_min|default:"-" }} - ${{ job.salary_max|default:"-" }}</span></li>
                        {% endif %}
                        {% if job.application_deadline %}
                        <li class="mb-2"><span class="text-muted d-block small">Deadline</span><span class="fw-medium">{{ job.application_deadline|date:"M d, Y" }}</span></li>
                        {% endif %}
                        <li class="mb-0"><span class="text-muted d-block small">Posted</span><span class="fw-medium">{{ job.created_at|date:"M d, Y" }}</span></li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_application_form.html", """{% extends 'base.html' %}
{% block title %}Apply for {{ job.title }}{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm">
                    <h4 class="fw-bold mb-2">Apply for {{ job.title }}</h4>
                    <p class="text-muted small mb-4">at {{ job.startup.name }}</p>
                    <form method="post" enctype="multipart/form-data">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Resume (PDF, DOCX)</label>
                            {{ form.resume }}
                            {% if form.resume.errors %}<div class="text-danger small mt-1">{{ form.resume.errors }}</div>{% endif %}
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Cover Letter (Optional)</label>
                            {{ form.cover_letter }}
                            {% if form.cover_letter.errors %}<div class="text-danger small mt-1">{{ form.cover_letter.errors }}</div>{% endif %}
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-medium">Portfolio URL (Optional)</label>
                            {{ form.portfolio_url }}
                            {% if form.portfolio_url.errors %}<div class="text-danger small mt-1">{{ form.portfolio_url.errors }}</div>{% endif %}
                        </div>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Submit Application</button>
                            <a href="{% url 'incubator:job_posting_detail' job.id %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_application_list.html", """{% extends 'base.html' %}
{% block title %}Job Applications{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Job Applications</h4>
        </div>
        
        <div class="card border-0 shadow-sm p-3">
            <div class="table-responsive">
                <table class="table align-middle">
                    <thead>
                        <tr>
                            <th>Job Title</th>
                            <th>Startup</th>
                            <th>Applicant</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for app in applications %}
                        <tr>
                            <td class="fw-medium">{{ app.job.title }}</td>
                            <td>{{ app.job.startup.name }}</td>
                            <td>{{ app.applicant.get_full_name|default:app.applicant.username }}</td>
                            <td>
                                {% if app.status == 'submitted' %}<span class="badge bg-warning text-dark">Submitted</span>
                                {% elif app.status == 'reviewing' %}<span class="badge bg-info">Reviewing</span>
                                {% elif app.status == 'shortlisted' %}<span class="badge bg-primary">Shortlisted</span>
                                {% elif app.status == 'interview' %}<span class="badge bg-primary">Interview</span>
                                {% elif app.status == 'rejected' %}<span class="badge bg-danger">Rejected</span>
                                {% elif app.status == 'hired' %}<span class="badge bg-success">Hired</span>
                                {% else %}<span class="badge bg-secondary">{{ app.get_status_display }}</span>{% endif %}
                            </td>
                            <td class="text-muted small">{{ app.applied_at|date:"M d, Y" }}</td>
                            <td><a href="{% url 'incubator:job_application_detail' app.id %}" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="6" class="text-center text-muted py-5">No applications found.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "job_application_detail.html", """{% extends 'base.html' %}
{% block title %}Application Details{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="mb-3">
            <a href="{% url 'incubator:job_application_list' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Applications
            </a>
        </div>
        
        <div class="row g-4">
            <div class="col-md-8">
                <div class="card p-4 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h4 class="fw-bold mb-1">Application for {{ app.job.title }}</h4>
                            <p class="text-muted mb-0">by {{ app.applicant.get_full_name|default:app.applicant.username }}</p>
                        </div>
                        <div>
                            <span class="badge bg-primary px-3 py-2 fs-6 rounded-pill">{{ app.get_status_display }}</span>
                        </div>
                    </div>
                    
                    <div class="bg-light p-3 rounded mb-4 d-flex gap-3">
                        <a href="{{ app.resume.url }}" class="btn btn-outline-primary" target="_blank"><i class="bi bi-file-earmark-pdf me-1"></i> View Resume</a>
                        {% if app.portfolio_url %}
                        <a href="{{ app.portfolio_url }}" class="btn btn-outline-secondary" target="_blank"><i class="bi bi-link-45deg me-1"></i> Portfolio</a>
                        {% endif %}
                    </div>
                    
                    {% if app.cover_letter %}
                    <h6 class="fw-bold mb-2">Cover Letter</h6>
                    <div class="p-3 bg-light rounded text-muted mb-4" style="white-space: pre-wrap;">{{ app.cover_letter }}</div>
                    {% endif %}
                    
                    {% if is_owner %}
                    <div class="border-top pt-4 mt-4">
                        <h6 class="fw-bold mb-3">Update Application Status</h6>
                        <form method="post" class="d-flex flex-wrap gap-2">
                            {% csrf_token %}
                            <button type="submit" name="status" value="reviewing" class="btn btn-outline-secondary btn-sm">Mark Reviewing</button>
                            <button type="submit" name="status" value="shortlisted" class="btn btn-outline-primary btn-sm">Shortlist</button>
                            <button type="submit" name="status" value="interview" class="btn btn-outline-info btn-sm">Mark Interview</button>
                            <button type="submit" name="status" value="hired" class="btn btn-success btn-sm">Hire Candidate</button>
                            <button type="submit" name="status" value="rejected" class="btn btn-danger btn-sm">Reject</button>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card p-3 border-0 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-0">Interviews</h6>
                        {% if is_owner %}
                        <a href="{% url 'incubator:interview_create' app.id %}" class="btn btn-sm btn-primary">Schedule</a>
                        {% endif %}
                    </div>
                    
                    <ul class="list-group list-group-flush">
                        {% for interview in interviews %}
                        <li class="list-group-item px-0 border-bottom">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="fw-medium text-truncate">{{ interview.scheduled_at|date:"M d, Y H:i" }}</span>
                                <span class="badge bg-secondary bg-opacity-10 text-secondary">{{ interview.get_status_display }}</span>
                            </div>
                            <small class="text-muted d-block">{{ interview.get_meeting_type_display }} • {{ interview.duration }}m</small>
                            {% if interview.meeting_link %}
                            <a href="{{ interview.meeting_link }}" target="_blank" class="small mt-1 d-inline-block">Join Link</a>
                            {% endif %}
                        </li>
                        {% empty %}
                        <li class="list-group-item px-0 text-muted small border-0">No interviews scheduled.</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(base + "interview_form.html", """{% extends 'base.html' %}
{% block title %}Schedule Interview{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-0 shadow-sm">
                    <h5 class="fw-bold mb-2">Schedule Interview</h5>
                    <p class="text-muted small mb-4">For candidate {{ app.applicant.username }}</p>
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
                            <button type="submit" class="btn btn-primary px-4 fw-medium">Schedule Interview</button>
                            <a href="{% url 'incubator:job_application_detail' app.id %}" class="btn btn-light border">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

# ----------------- DASHBOARDS -----------------

create_file(dbase + "investor_dashboard.html", """{% extends 'base.html' %}
{% block title %}Investor Dashboard{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Welcome, {{ request.user.username }}</h4>
            {% if not profile_exists %}
            <a href="{% url 'incubator:investor_profile_edit' %}" class="btn btn-primary fw-medium">Complete Your Profile</a>
            {% else %}
            <a href="{% url 'incubator:investor_directory' %}" class="btn btn-outline-primary fw-medium">Find Startups</a>
            {% endif %}
        </div>

        <div class="row g-4">
            <div class="col-md-8">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                        <h6 class="fw-bold mb-0">Open Funding Opportunities</h6>
                        <a href="{% url 'incubator:funding_round_list' %}" class="small text-decoration-none">View All</a>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            {% for round in open_rounds %}
                            <a href="{% url 'incubator:funding_round_detail' round.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <h6 class="mb-0 fw-bold">{{ round.round_name }}</h6>
                                    <span class="badge bg-primary bg-opacity-10 text-primary">{{ round.get_round_type_display }}</span>
                                </div>
                                <p class="text-muted small mb-0">{{ round.startup.name }} • Target: ${{ round.target_amount }}</p>
                            </a>
                            {% empty %}
                            <p class="text-muted small py-3 mb-0">No open funding rounds currently available.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                        <h6 class="fw-bold mb-0">My Applications</h6>
                        <a href="{% url 'incubator:funding_application_list' %}" class="small text-decoration-none">View All</a>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            {% for app in my_apps %}
                            <a href="{% url 'incubator:funding_application_detail' app.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <h6 class="mb-0 fw-bold">{{ app.funding_round.startup.name }}</h6>
                                    {% if app.status == 'pending' %}<span class="badge bg-warning text-dark">Pending</span>
                                    {% elif app.status == 'accepted' %}<span class="badge bg-success">Accepted</span>
                                    {% else %}<span class="badge bg-secondary">{{ app.get_status_display }}</span>{% endif %}
                                </div>
                                <p class="text-muted small mb-0">Requested: ${{ app.requested_amount }} • {{ app.created_at|date:"M d, Y" }}</p>
                            </a>
                            {% empty %}
                            <p class="text-muted small py-3 mb-0">You haven't applied to any rounds yet.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                        <h6 class="fw-bold mb-0">Upcoming Meetings</h6>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            {% for meeting in upcoming_meetings %}
                            <a href="{% url 'incubator:investor_meeting_detail' meeting.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                <h6 class="mb-1 text-truncate fw-medium">{{ meeting.funding_application.funding_round.startup.name }}</h6>
                                <small class="text-muted d-block"><i class="bi bi-clock me-1"></i> {{ meeting.scheduled_at|date:"M d, Y H:i" }}</small>
                            </a>
                            {% empty %}
                            <p class="text-muted small py-2 mb-0">No upcoming meetings.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

create_file(dbase + "applicant_dashboard.html", """{% extends 'base.html' %}
{% block title %}Applicant Dashboard{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Applicant Dashboard</h4>
            <a href="{% url 'incubator:job_directory' %}" class="btn btn-primary fw-medium">Find Jobs</a>
        </div>

        <div class="row g-4">
            <div class="col-md-8">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                        <h6 class="fw-bold mb-0">My Applications</h6>
                        <a href="{% url 'incubator:job_application_list' %}" class="small text-decoration-none">View All</a>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            {% for app in my_apps %}
                            <a href="{% url 'incubator:job_application_detail' app.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <h6 class="mb-0 fw-bold">{{ app.job.title }}</h6>
                                    <span class="badge bg-secondary bg-opacity-10 text-secondary">{{ app.get_status_display }}</span>
                                </div>
                                <p class="text-muted small mb-0">{{ app.job.startup.name }} • Applied {{ app.applied_at|date:"M d, Y" }}</p>
                            </a>
                            {% empty %}
                            <p class="text-muted small py-3 mb-0">You haven't submitted any job applications yet.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                        <h6 class="fw-bold mb-0">Upcoming Interviews</h6>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            {% for interview in upcoming_interviews %}
                            <li class="list-group-item px-0 border-bottom">
                                <h6 class="mb-1 text-truncate fw-medium">{{ interview.application.job.title }}</h6>
                                <small class="text-muted d-block"><i class="bi bi-clock me-1"></i> {{ interview.scheduled_at|date:"M d, Y H:i" }}</small>
                                {% if interview.meeting_link %}
                                <a href="{{ interview.meeting_link }}" target="_blank" class="small mt-1 d-inline-block">Join Link</a>
                                {% endif %}
                            </li>
                            {% empty %}
                            <p class="text-muted small py-2 mb-0">No upcoming interviews.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
{% endblock %}""")

print("Done generating extra templates script.")
