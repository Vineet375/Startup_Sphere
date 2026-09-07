import os

file_path = 'templates/dashboard/home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the Empty state for startup
old_empty = """        <div class="card p-5 text-center shadow-sm border-0">
            <div class="mb-4">
                <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                    <i class="bi bi-rocket-takeoff" style="font-size: 2.5rem;"></i>
                </div>
            </div>
            <h4 class="fw-bold mb-3">Welcome to StartupSphere</h4>
            <p class="text-muted mb-4 mx-auto" style="max-width: 500px;">You haven't registered a startup yet. Get started by setting up your startup profile to begin your incubation journey.</p>
            <div>
                <a href="{% url 'incubator:register_startup' %}" class="btn btn-primary px-4 fw-medium">Register Startup</a>
            </div>
        </div>"""

new_empty = """        <div class="card p-5 text-center shadow-sm border-0">
            <div class="mb-4">
                <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                    <i class="bi bi-rocket-takeoff" style="font-size: 2.5rem;"></i>
                </div>
            </div>
            <h4 class="fw-bold mb-3">Welcome to StartupSphere</h4>
            {% if request.user.role == 'founder' %}
            <p class="text-muted mb-4 mx-auto" style="max-width: 500px;">You haven't registered a startup yet. Get started by setting up your startup profile to begin your incubation journey.</p>
            <div>
                <a href="{% url 'incubator:register_startup' %}" class="btn btn-primary px-4 fw-medium">Register Startup</a>
            </div>
            {% else %}
            <p class="text-muted mb-4 mx-auto" style="max-width: 500px;">You are not associated with any startup yet. If you were invited by a founder, please wait for them to add you to their team.</p>
            {% endif %}
        </div>"""

if old_empty in content:
    content = content.replace(old_empty, new_empty)

# Fix Quick actions
old_quick_actions = """                    <a href="{% url 'incubator:idea_create' %}" class="d-flex justify-content-between align-items-center mb-3 text-decoration-none text-main border rounded p-2 hover-bg-light">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-lightbulb text-primary"></i>
                            <span class="small fw-medium">Draft New Idea</span>
                        </div>
                        <i class="bi bi-arrow-right text-muted"></i>
                    </a>
                    
                    <a href="{% url 'incubator:startup_detail' %}" class="d-flex justify-content-between align-items-center mb-3 text-decoration-none text-main border rounded p-2 hover-bg-light">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-rocket text-success"></i>
                            <span class="small fw-medium">Manage Startup Profile</span>
                        </div>
                        <i class="bi bi-arrow-right text-muted"></i>
                    </a>"""

new_quick_actions = """                    {% if request.user == startup.founder %}
                    <a href="{% url 'incubator:idea_create' %}" class="d-flex justify-content-between align-items-center mb-3 text-decoration-none text-main border rounded p-2 hover-bg-light">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-lightbulb text-primary"></i>
                            <span class="small fw-medium">Draft New Idea</span>
                        </div>
                        <i class="bi bi-arrow-right text-muted"></i>
                    </a>
                    
                    <a href="{% url 'incubator:startup_edit' %}" class="d-flex justify-content-between align-items-center mb-3 text-decoration-none text-main border rounded p-2 hover-bg-light">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-rocket text-success"></i>
                            <span class="small fw-medium">Edit Startup Profile</span>
                        </div>
                        <i class="bi bi-arrow-right text-muted"></i>
                    </a>
                    {% endif %}
                    
                    <a href="{% url 'incubator:startup_detail' %}" class="d-flex justify-content-between align-items-center mb-3 text-decoration-none text-main border rounded p-2 hover-bg-light">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-rocket text-success"></i>
                            <span class="small fw-medium">View Startup Workspace</span>
                        </div>
                        <i class="bi bi-arrow-right text-muted"></i>
                    </a>"""

if old_quick_actions in content:
    content = content.replace(old_quick_actions, new_quick_actions)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
