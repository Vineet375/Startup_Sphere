import os

templates_dir = 'templates/incubator'

dir_html = """{% extends 'base.html' %}
{% block title %}Startup Directory | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="fw-bold m-0">Startup Directory</h3>
        </div>
        
        <div class="card shadow-sm border-0 mb-4 p-3">
            <form method="get" class="row g-3 align-items-end">
                <div class="col-md-4">
                    <label class="form-label text-muted small fw-bold">Search</label>
                    <input type="text" name="q" class="form-control" placeholder="Name, tagline, industry..." value="{{ q|default:'' }}">
                </div>
                <div class="col-md-3">
                    <label class="form-label text-muted small fw-bold">Industry</label>
                    <input type="text" name="industry" class="form-control" placeholder="e.g. Fintech" value="{{ industry|default:'' }}">
                </div>
                <div class="col-md-3">
                    <label class="form-label text-muted small fw-bold">Status</label>
                    <select name="status" class="form-select">
                        <option value="">Any Status</option>
                        <option value="incubating" {% if status == 'incubating' %}selected{% endif %}>Incubating</option>
                        <option value="graduated" {% if status == 'graduated' %}selected{% endif %}>Graduated</option>
                        <option value="dropped" {% if status == 'dropped' %}selected{% endif %}>Dropped</option>
                    </select>
                </div>
                <div class="col-md-2 d-grid gap-2 d-md-flex">
                    <button type="submit" class="btn btn-primary w-100">Filter</button>
                    <a href="{% url 'incubator:startup_directory' %}" class="btn btn-outline-secondary w-100">Clear</a>
                </div>
            </form>
        </div>

        <div class="row row-cols-1 row-cols-md-3 g-4">
            {% for startup in startups %}
            <div class="col">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            {% if startup.logo %}
                                <img src="{{ startup.logo.url }}" class="rounded-circle me-3" style="width: 50px; height: 50px; object-fit: cover;">
                            {% else %}
                                <div class="bg-secondary bg-opacity-10 text-secondary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                    <i class="bi bi-building fs-4"></i>
                                </div>
                            {% endif %}
                            <div>
                                <h5 class="card-title fw-bold m-0">{{ startup.name }}</h5>
                                <small class="text-muted">{{ startup.industry|default:"No Industry" }}</small>
                            </div>
                        </div>
                        <p class="card-text text-muted">{{ startup.tagline|default:"No tagline provided." }}</p>
                    </div>
                    <div class="card-footer bg-white border-0 pt-0 d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary rounded-pill">{{ startup.get_status_display }}</span>
                        <a href="{% url 'incubator:startup_public_profile' startup.id %}" class="btn btn-sm btn-outline-primary">View Profile</a>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <i class="bi bi-search text-muted fs-1 d-block mb-3"></i>
                <p class="text-muted mb-0">No startups found matching your criteria.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}
"""

profile_html = """{% extends 'base.html' %}
{% block title %}{{ startup.name }} | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        
        <div class="mb-3">
            <a href="{% url 'incubator:startup_directory' %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Directory
            </a>
        </div>

        <div class="card border-0 shadow-sm p-5">
            <div class="row align-items-center text-center text-md-start">
                <div class="col-md-2 mb-4 mb-md-0 d-flex justify-content-center">
                    {% if startup.logo %}
                        <img src="{{ startup.logo.url }}" class="rounded-circle shadow-sm" style="width: 120px; height: 120px; object-fit: cover;">
                    {% else %}
                        <div class="bg-secondary bg-opacity-10 text-secondary rounded-circle d-flex align-items-center justify-content-center" style="width: 120px; height: 120px;">
                            <i class="bi bi-building" style="font-size: 3rem;"></i>
                        </div>
                    {% endif %}
                </div>
                <div class="col-md-10">
                    <h2 class="fw-bold mb-1">{{ startup.name }}</h2>
                    <h5 class="text-muted mb-3">{{ startup.tagline|default:"" }}</h5>
                    <div class="d-flex flex-wrap gap-2 justify-content-center justify-content-md-start">
                        <span class="badge bg-light text-dark border"><i class="bi bi-tag me-1"></i>{{ startup.industry|default:"Uncategorized" }}</span>
                        <span class="badge bg-primary"><i class="bi bi-activity me-1"></i>{{ startup.get_status_display }}</span>
                    </div>
                </div>
            </div>
            
            <hr class="my-4">
            
            <div class="row">
                <div class="col-md-8">
                    <h5 class="fw-bold mb-3">About the Startup</h5>
                    <p class="text-secondary" style="white-space: pre-line;">{{ startup.description|default:"No detailed description provided." }}</p>
                </div>
                <div class="col-md-4">
                    <div class="bg-light p-4 rounded text-center">
                        <div class="mb-3">
                            <div class="bg-white rounded-circle shadow-sm d-inline-flex align-items-center justify-content-center mb-2" style="width: 60px; height: 60px;">
                                {% if startup.founder.avatar %}
                                    <img src="{{ startup.founder.avatar.url }}" class="rounded-circle w-100 h-100 object-fit-cover">
                                {% else %}
                                    <i class="bi bi-person fs-3 text-secondary"></i>
                                {% endif %}
                            </div>
                            <h6 class="fw-bold m-0">{{ startup.founder.get_full_name|default:startup.founder.username }}</h6>
                            <small class="text-muted">Founder</small>
                        </div>
                        <a href="mailto:{{ startup.founder.email }}" class="btn btn-outline-primary btn-sm w-100"><i class="bi bi-envelope me-1"></i> Contact</a>
                    </div>
                </div>
            </div>
        </div>

    </main>
</div>
{% endblock %}
"""

eval_list_html = """{% extends 'base.html' %}
{% block title %}Evaluations for {{ startup.name }} | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 bg-light" style="overflow-y: auto;">
        
        <div class="mb-3">
            <a href="{% if is_founder or is_assigned_mentor %}{% url 'incubator:startup_detail_id' startup.id %}{% else %}{% url 'incubator:startup_directory' %}{% endif %}" class="text-decoration-none text-muted">
                <i class="bi bi-arrow-left me-1"></i> Back to Workspace
            </a>
        </div>

        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="fw-bold m-0">Performance & Evaluations</h3>
            {% if is_assigned_mentor and not user_evaluation %}
                <a href="{% url 'incubator:evaluation_create' startup.id %}" class="btn btn-primary"><i class="bi bi-plus-lg me-1"></i> Create Evaluation</a>
            {% elif is_assigned_mentor and user_evaluation %}
                <a href="{% url 'incubator:evaluation_edit' user_evaluation.id %}" class="btn btn-outline-primary"><i class="bi bi-pencil me-1"></i> Edit My Evaluation</a>
            {% endif %}
        </div>
        
        <!-- Summary Card -->
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4 text-center">
                <h5 class="fw-bold mb-3 text-muted">Overall Startup Performance</h5>
                {% if avg_overall %}
                    <div class="display-3 fw-bold text-primary mb-2">{{ avg_overall|floatformat:1 }}<span class="fs-4 text-muted">/10</span></div>
                    <p class="text-muted mb-0">Based on {{ evaluations.count }} evaluation{{ evaluations.count|pluralize }}</p>
                {% else %}
                    <div class="display-4 fw-bold text-muted mb-2">- / 10</div>
                    <p class="text-muted mb-0">No evaluations have been submitted yet.</p>
                {% endif %}
            </div>
        </div>

        <!-- Evaluation List -->
        <h5 class="fw-bold mb-3">Evaluation History</h5>
        <div class="row row-cols-1 g-4">
            {% for eval in evaluations %}
            <div class="col">
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-white border-bottom-0 pt-3 pb-0 d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <div class="bg-light text-primary rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 40px; height: 40px;">
                                <i class="bi bi-clipboard-data"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold m-0">{{ eval.evaluator.get_full_name|default:eval.evaluator.username }}</h6>
                                <small class="text-muted">{{ eval.updated_at|date:"M d, Y" }}</small>
                            </div>
                        </div>
                        <div class="text-end">
                            <h4 class="fw-bold text-primary m-0">{{ eval.overall_score|floatformat:1 }} <span class="fs-6 text-muted">/10</span></h4>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3 g-2">
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Innovation</small><strong class="fs-5">{{ eval.innovation_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Market</small><strong class="fs-5">{{ eval.market_potential_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Business</small><strong class="fs-5">{{ eval.business_model_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Team</small><strong class="fs-5">{{ eval.team_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Execution</small><strong class="fs-5">{{ eval.execution_score }}</strong></div></div>
                        </div>
                        {% if eval.comments %}
                            <div class="bg-light p-3 rounded text-secondary fst-italic">
                                "{{ eval.comments }}"
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <i class="bi bi-clipboard-x text-muted fs-1 d-block mb-3"></i>
                <p class="text-muted mb-0">No evaluations found.</p>
            </div>
            {% endfor %}
        </div>
    </main>
</div>
{% endblock %}
"""

eval_form_html = """{% extends 'base.html' %}
{% block title %}{% if evaluation %}Edit{% else %}Create{% endif %} Evaluation | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 d-flex justify-content-center align-items-start" style="overflow-y: auto;">
        <div class="card p-4 shadow-sm w-100 mt-4" style="max-width: 700px;">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="fw-bold m-0">{% if evaluation %}Edit Evaluation{% else %}Evaluate Startup{% endif %}</h4>
                <span class="badge bg-light text-dark border">{{ startup.name }}</span>
            </div>
            
            <form method="post">
                {% csrf_token %}
                
                <div class="alert alert-info py-2 small">
                    <i class="bi bi-info-circle me-1"></i> Rate the startup across these 5 dimensions on a scale of 1 to 10. The overall score will be calculated automatically.
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6 mb-3 mb-md-0">
                        <label class="form-label fw-medium">Innovation Score (1-10)</label>
                        {{ form.innovation_score }}
                        {% if form.innovation_score.errors %}<div class="text-danger small mt-1">{{ form.innovation_score.errors }}</div>{% endif %}
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-medium">Market Potential Score (1-10)</label>
                        {{ form.market_potential_score }}
                        {% if form.market_potential_score.errors %}<div class="text-danger small mt-1">{{ form.market_potential_score.errors }}</div>{% endif %}
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6 mb-3 mb-md-0">
                        <label class="form-label fw-medium">Business Model Score (1-10)</label>
                        {{ form.business_model_score }}
                        {% if form.business_model_score.errors %}<div class="text-danger small mt-1">{{ form.business_model_score.errors }}</div>{% endif %}
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-medium">Team Score (1-10)</label>
                        {{ form.team_score }}
                        {% if form.team_score.errors %}<div class="text-danger small mt-1">{{ form.team_score.errors }}</div>{% endif %}
                    </div>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <label class="form-label fw-medium">Execution Score (1-10)</label>
                        {{ form.execution_score }}
                        {% if form.execution_score.errors %}<div class="text-danger small mt-1">{{ form.execution_score.errors }}</div>{% endif %}
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-medium">Comments (Optional)</label>
                    {{ form.comments }}
                    {% if form.comments.errors %}<div class="text-danger small mt-1">{{ form.comments.errors }}</div>{% endif %}
                </div>
                
                <div class="d-flex gap-2 justify-content-end">
                    <a href="{% url 'incubator:evaluation_list' startup.id %}" class="btn btn-outline-secondary">Cancel</a>
                    <button type="submit" class="btn btn-primary">Save Evaluation</button>
                </div>
            </form>
        </div>
    </main>
</div>
{% endblock %}
"""

with open(f'{templates_dir}/startup_directory.html', 'w', encoding='utf-8') as f: f.write(dir_html)
with open(f'{templates_dir}/startup_public_profile.html', 'w', encoding='utf-8') as f: f.write(profile_html)
with open(f'{templates_dir}/evaluation_list.html', 'w', encoding='utf-8') as f: f.write(eval_list_html)
with open(f'{templates_dir}/evaluation_form.html', 'w', encoding='utf-8') as f: f.write(eval_form_html)
