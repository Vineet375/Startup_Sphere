import os

team_edit_html = """{% extends 'base.html' %}
{% block title %}Edit Team Member | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 d-flex justify-content-center align-items-start" style="overflow-y: auto;">
        <div class="card p-4 shadow-sm w-100 mt-4" style="max-width: 600px;">
            <h4 class="fw-bold mb-4">Edit Team Member</h4>
            
            <div class="mb-4 p-3 bg-light rounded d-flex align-items-center">
                <div class="bg-secondary bg-opacity-10 text-secondary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 45px; height: 45px;">
                    <i class="bi bi-person fs-4"></i>
                </div>
                <div>
                    {% if team_member.user %}
                        <h6 class="mb-0 fw-bold">{{ team_member.user.get_full_name|default:team_member.user.username }}</h6>
                        <small class="text-muted">{{ team_member.user.email }}</small>
                    {% else %}
                        <h6 class="mb-0 fw-bold text-muted">{{ team_member.invited_email }}</h6>
                        <small class="text-muted">Pending Invitation</small>
                    {% endif %}
                </div>
            </div>

            <form method="post">
                {% csrf_token %}
                
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
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        </div>
    </main>
</div>
{% endblock %}
"""

document_edit_html = """{% extends 'base.html' %}
{% block title %}Edit Document | StartupSphere{% endblock %}
{% block layout %}
<div class="d-flex" style="min-height: calc(100vh - 65px);">
    {% include 'dashboard/_sidebar.html' %}
    <main class="flex-grow-1 p-4 d-flex justify-content-center align-items-start" style="overflow-y: auto;">
        <div class="card p-4 shadow-sm w-100 mt-4" style="max-width: 600px;">
            <h4 class="fw-bold mb-4">Edit Document</h4>
            
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
                    <label class="form-label fw-medium">File (Optional: Upload a new file to replace the existing one)</label>
                    {{ form.file }}
                    <small class="text-muted d-block mt-1">Allowed formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX (Max 5MB)</small>
                    <small class="text-muted d-block mt-1">Current file: <a href="{{ document.file.url }}" target="_blank">{{ document.file.name }}</a></small>
                    {% if form.file.errors %}<div class="text-danger small mt-1">{{ form.file.errors }}</div>{% endif %}
                </div>
                
                <div class="d-flex gap-2 justify-content-end">
                    <a href="{% url 'incubator:document_list' %}" class="btn btn-outline-secondary">Cancel</a>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        </div>
    </main>
</div>
{% endblock %}
"""

with open('templates/incubator/team_member_edit.html', 'w', encoding='utf-8') as f:
    f.write(team_edit_html)
    
with open('templates/incubator/document_edit.html', 'w', encoding='utf-8') as f:
    f.write(document_edit_html)
