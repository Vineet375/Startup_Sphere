import os

home_path = 'templates/dashboard/home.html'
with open(home_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

# Add Funding & Hiring sections to home.html
funding_hiring_html = """
    <div class="row mt-4">
        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                    <h6 class="fw-bold mb-0">Active Funding Rounds</h6>
                    <a href="{% url 'incubator:funding_round_list' %}" class="text-decoration-none small">View All</a>
                </div>
                <div class="card-body">
                    {% if active_rounds %}
                        <div class="list-group list-group-flush">
                            {% for round in active_rounds %}
                                <a href="{% url 'incubator:funding_round_detail' round.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                    <div class="d-flex justify-content-between w-100">
                                        <h6 class="mb-1 fw-bold">{{ round.round_name }}</h6>
                                        <small class="text-success fw-medium">${{ round.raised_amount }} raised</small>
                                    </div>
                                    <small class="text-muted d-block text-truncate">Target: ${{ round.target_amount }}</small>
                                </a>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted small mb-0 mt-2">No active funding rounds.</p>
                        <a href="{% url 'incubator:funding_round_create' %}" class="btn btn-sm btn-outline-primary mt-2">Create Round</a>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                    <h6 class="fw-bold mb-0">Hiring & Jobs</h6>
                    <a href="{% url 'incubator:job_posting_list' %}" class="text-decoration-none small">View All</a>
                </div>
                <div class="card-body">
                    {% if active_jobs %}
                        <div class="list-group list-group-flush">
                            {% for job in active_jobs %}
                                <a href="{% url 'incubator:job_posting_detail' job.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                    <div class="d-flex justify-content-between w-100">
                                        <h6 class="mb-1 fw-bold">{{ job.title }}</h6>
                                        <small class="text-primary fw-medium">{{ job.get_employment_type_display }}</small>
                                    </div>
                                </a>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted small mb-0 mt-2">No active job postings.</p>
                        <a href="{% url 'incubator:job_posting_create' %}" class="btn btn-sm btn-outline-primary mt-2">Post a Job</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
"""

if "Active Funding Rounds" not in home_content:
    home_content = home_content.replace("{% endblock layout %}", funding_hiring_html + "\n{% endblock layout %}")
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(home_content)

# Admin Dashboard
admin_path = 'templates/dashboard/admin_dashboard.html'
with open(admin_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

admin_batch8_html = """
        <h5 class="fw-bold mt-5 mb-4 text-secondary">Funding & Talent KPIs</h5>
        <div class="row g-4 mb-5">
            <div class="col-md-3">
                <div class="card bg-primary text-white border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="fw-medium opacity-75 mb-1">Total Target</h6>
                    <h2 class="fw-bold mb-0">${{ total_target }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="fw-medium opacity-75 mb-1">Total Raised</h6>
                    <h2 class="fw-bold mb-0">${{ total_raised }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Open Rounds</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ open_rounds }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Funding Apps</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ total_funding_apps }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Job Postings</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ total_jobs }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Job Applications</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ total_job_apps }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Shortlisted</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ shortlisted_job_apps }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-0 shadow-sm text-center p-3 h-100">
                    <h6 class="text-muted fw-medium mb-1">Total Interviews</h6>
                    <h2 class="text-dark fw-bold mb-0">{{ total_interviews }}</h2>
                </div>
            </div>
        </div>
"""

if "Funding & Talent KPIs" not in admin_content:
    # insert before <div class="row g-4"> that holds Recent Activity
    admin_content = admin_content.replace('<h5 class="fw-bold mb-4 text-secondary">Recent Platform Activity</h5>', admin_batch8_html + '\n        <h5 class="fw-bold mb-4 text-secondary">Recent Platform Activity</h5>')
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(admin_content)

