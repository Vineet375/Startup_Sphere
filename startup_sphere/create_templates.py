import os

os.makedirs('templates/incubator', exist_ok=True)

team_list_html = """{% extends 'base.html' %}
{% block title %}My Team | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">{% if request.user == startup.founder or request.user.role == 'mentor' or request.user.role == 'admin' %}{{ startup.name }} Team{% else %}My Team{% endif %}</h4>
            {% if request.user == startup.founder %}
            <a href="{% url 'incubator:team_invite' %}" class="btn btn-primary btn-sm fw-medium">
                <i class="bi bi-person-plus me-1"></i> Invite Member
            </a>
            {% endif %}
        </div>
        
        <div class="card p-4">
            <h5 class="fw-bold mb-3">Founder</h5>
            <div class="list-group mb-4">
                <div class="list-group-item d-flex justify-content-between align-items-center p-3">
                    <div class="d-flex align-items-center">
                        <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 45px; height: 45px;">
                            <i class="bi bi-person-fill fs-4"></i>
                        </div>
                        <div>
                            <h6 class="mb-0 fw-bold">{{ startup.founder.get_full_name|default:startup.founder.username }}</h6>
                            <small class="text-muted">{{ startup.founder.email }}</small>
                        </div>
                    </div>
                    <div>
                        <span class="badge bg-success">Founder & Owner</span>
                    </div>
                </div>
            </div>

            <h5 class="fw-bold mb-3">Team Members</h5>
            {% if team_members %}
                <div class="list-group">
                {% for member in team_members %}
                    <div class="list-group-item d-flex justify-content-between align-items-center p-3">
                        <div class="d-flex align-items-center">
                            <div class="bg-secondary bg-opacity-10 text-secondary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 45px; height: 45px;">
                                <i class="bi bi-person fs-4"></i>
                            </div>
                            <div>
                                {% if member.user %}
                                    <h6 class="mb-0 fw-bold">{{ member.user.get_full_name|default:member.user.username }}</h6>
                                    <small class="text-muted">{{ member.user.email }}</small>
                                {% else %}
                                    <h6 class="mb-0 fw-bold text-muted">{{ member.invited_email }}</h6>
                                    <small class="text-muted">Awaiting Registration</small>
                                {% endif %}
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <div>
                                <span class="badge bg-light text-dark border">{{ member.get_position_display }}</span>
                                {% if member.status == 'pending' %}
                                    <span class="badge bg-warning text-dark ms-1">Pending</span>
                                {% else %}
                                    <span class="badge bg-success ms-1">Active</span>
                                {% endif %}
                            </div>
                            
                            {% if request.user == startup.founder %}
                                <form action="{% url 'incubator:team_remove' member.id %}" method="post" class="m-0" onsubmit="return confirm('Are you sure you want to remove this team member?');">
                                    {% csrf_token %}
                                    <button type="submit" class="btn btn-sm btn-outline-danger"><i class="bi bi-person-x"></i></button>
                                </form>
                            {% endif %}
                        </div>
                    </div>
                {% endfor %}
                </div>
            {% else %}
                <div class="text-center py-5 bg-light rounded">
                    <i class="bi bi-people text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-3 mb-0">Your startup team currently consists of you. Add team members to start building your team.</p>
                </div>
            {% endif %}
        </div>
    </main>
</div>
{% endblock %}
"""

team_invite_html = """{% extends 'base.html' %}
{% block title %}Invite Team Member | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 d-flex justify-content-center align-items-start" style="overflow-y: auto;">
        <div class="card p-4 shadow-sm w-100 mt-4" style="max-width: 600px;">
            <h4 class="fw-bold mb-4">Invite Team Member</h4>
            <form method="post">
                {% csrf_token %}
                <div class="mb-3">
                    <label class="form-label fw-medium">Email Address</label>
                    {{ form.email }}
                    <small class="text-muted d-block mt-1">If they already have an account, they'll be added immediately. Otherwise, an invitation will be recorded.</small>
                    {% if form.email.errors %}
                        <div class="text-danger small mt-1">{{ form.email.errors }}</div>
                    {% endif %}
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-medium">Position</label>
                    {{ form.position }}
                    {% if form.position.errors %}
                        <div class="text-danger small mt-1">{{ form.position.errors }}</div>
                    {% endif %}
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-medium">Custom Position (Optional)</label>
                    {{ form.custom_position }}
                    {% if form.custom_position.errors %}
                        <div class="text-danger small mt-1">{{ form.custom_position.errors }}</div>
                    {% endif %}
                </div>
                
                <div class="d-flex gap-2 justify-content-end">
                    <a href="{% url 'incubator:team_list' %}" class="btn btn-outline-secondary">Cancel</a>
                    <button type="submit" class="btn btn-primary">Send Invitation</button>
                </div>
            </form>
        </div>
    </main>
</div>
{% endblock %}
"""

document_list_html = """{% extends 'base.html' %}
{% block title %}Documents | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4" style="overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Documents & Resources</h4>
            {% if request.user == startup.founder %}
            <a href="{% url 'incubator:document_upload' %}" class="btn btn-primary btn-sm fw-medium">
                <i class="bi bi-upload me-1"></i> Upload Document
            </a>
            {% endif %}
        </div>
        
        <div class="card p-0 overflow-hidden">
            <div class="bg-light p-3 border-bottom d-flex gap-2 overflow-auto" style="white-space: nowrap;">
                <a href="?category=" class="btn btn-sm {% if not current_category %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">All Documents</a>
                <a href="?category=pitch_deck" class="btn btn-sm {% if current_category == 'pitch_deck' %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">Pitch Decks</a>
                <a href="?category=business_plan" class="btn btn-sm {% if current_category == 'business_plan' %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">Business Plans</a>
                <a href="?category=financial" class="btn btn-sm {% if current_category == 'financial' %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">Financial</a>
                <a href="?category=legal" class="btn btn-sm {% if current_category == 'legal' %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">Legal</a>
                <a href="?category=product" class="btn btn-sm {% if current_category == 'product' %}btn-primary{% else %}btn-outline-secondary{% endif %} rounded-pill">Product</a>
            </div>
            
            <div class="p-4">
                {% if documents %}
                    <div class="row g-4">
                        {% for doc in documents %}
                        <div class="col-md-6 col-lg-4">
                            <div class="card h-100 border hover-shadow transition">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start mb-3">
                                        <div class="bg-primary bg-opacity-10 text-primary rounded p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                            <i class="bi bi-file-earmark-text fs-5"></i>
                                        </div>
                                        <span class="badge bg-light text-dark border">{{ doc.get_category_display }}</span>
                                    </div>
                                    <h6 class="fw-bold mb-2 text-truncate" title="{{ doc.title }}">{{ doc.title }}</h6>
                                    <p class="small text-muted mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; height: 3em;">
                                        {{ doc.description|default:"No description" }}
                                    </p>
                                    <div class="d-flex align-items-center text-muted small">
                                        <i class="bi bi-person me-1"></i> {{ doc.uploaded_by.get_full_name|default:doc.uploaded_by.username }}
                                    </div>
                                </div>
                                <div class="card-footer bg-white border-top d-flex justify-content-between align-items-center py-3">
                                    <small class="text-muted">{{ doc.created_at|date:"M d, Y" }}</small>
                                    <div class="d-flex gap-2">
                                        <a href="{{ doc.file.url }}" target="_blank" class="btn btn-sm btn-outline-primary" title="Download/View">
                                            <i class="bi bi-download"></i>
                                        </a>
                                        {% if request.user == startup.founder %}
                                        <form action="{% url 'incubator:document_delete' doc.id %}" method="post" class="m-0" onsubmit="return confirm('Delete this document?');">
                                            {% csrf_token %}
                                            <button type="submit" class="btn btn-sm btn-outline-danger" title="Delete">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </form>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="text-center py-5">
                        <i class="bi bi-folder-x text-muted" style="font-size: 3rem;"></i>
                        <p class="text-muted mt-3 mb-0">No documents have been uploaded yet. Keep your important startup resources organized here.</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>
</div>
{% endblock %}
"""

document_form_html = """{% extends 'base.html' %}
{% block title %}Upload Document | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 d-flex justify-content-center align-items-start" style="overflow-y: auto;">
        <div class="card p-4 shadow-sm w-100 mt-4" style="max-width: 600px;">
            <h4 class="fw-bold mb-4">Upload Document</h4>
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <div class="mb-3">
                    <label class="form-label fw-medium">Title</label>
                    {{ form.title }}
                    {% if form.title.errors %}<div class="text-danger small mt-1">{{ form.title.errors }}</div>{% endif %}
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-medium">Category</label>
                    {{ form.category }}
                    {% if form.category.errors %}<div class="text-danger small mt-1">{{ form.category.errors }}</div>{% endif %}
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-medium">Description (Optional)</label>
                    {{ form.description }}
                    {% if form.description.errors %}<div class="text-danger small mt-1">{{ form.description.errors }}</div>{% endif %}
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-medium">File (Max 5MB)</label>
                    {{ form.file }}
                    <small class="text-muted d-block mt-1">Allowed formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX</small>
                    {% if form.file.errors %}<div class="text-danger small mt-1">{{ form.file.errors }}</div>{% endif %}
                </div>
                
                <div class="d-flex gap-2 justify-content-end">
                    <a href="{% url 'incubator:document_list' %}" class="btn btn-outline-secondary">Cancel</a>
                    <button type="submit" class="btn btn-primary">Upload</button>
                </div>
            </form>
        </div>
    </main>
</div>
{% endblock %}
"""

with open('templates/incubator/team_list.html', 'w') as f:
    f.write(team_list_html)

with open('templates/incubator/team_invite.html', 'w') as f:
    f.write(team_invite_html)
    
with open('templates/incubator/document_list.html', 'w') as f:
    f.write(document_list_html)
    
with open('templates/incubator/document_form.html', 'w') as f:
    f.write(document_form_html)
