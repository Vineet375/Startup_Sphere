import os

file_path = 'templates/incubator/idea_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Hide Create Idea button
old_create_btn = """            <a href="{% url 'incubator:idea_create' %}" class="btn btn-primary fw-medium">
                <i class="bi bi-plus-lg me-1"></i> New Idea
            </a>"""

new_create_btn = """            {% if request.user == startup.founder %}
            <a href="{% url 'incubator:idea_create' %}" class="btn btn-primary fw-medium">
                <i class="bi bi-plus-lg me-1"></i> New Idea
            </a>
            {% endif %}"""

if old_create_btn in content:
    content = content.replace(old_create_btn, new_create_btn)

# Hide Edit/Submit for Team Members
old_actions = """                                            {% if idea.status == 'draft' %}
                                                <a href="{% url 'incubator:idea_edit' idea.id %}" class="btn btn-sm btn-light text-secondary" title="Edit Draft">
                                                    <i class="bi bi-pencil"></i>
                                                </a>
                                                <a href="{% url 'incubator:idea_submit' idea.id %}" class="btn btn-sm btn-light text-success" title="Submit Idea">
                                                    <i class="bi bi-send"></i>
                                                </a>
                                            {% endif %}"""

new_actions = """                                            {% if idea.status == 'draft' and request.user == startup.founder %}
                                                <a href="{% url 'incubator:idea_edit' idea.id %}" class="btn btn-sm btn-light text-secondary" title="Edit Draft">
                                                    <i class="bi bi-pencil"></i>
                                                </a>
                                                <a href="{% url 'incubator:idea_submit' idea.id %}" class="btn btn-sm btn-light text-success" title="Submit Idea">
                                                    <i class="bi bi-send"></i>
                                                </a>
                                            {% endif %}"""

if old_actions in content:
    content = content.replace(old_actions, new_actions)

# Hide Create Idea button in Empty State
old_empty_btn = """                    <p class="text-muted mb-4">Start drafting your first big idea to get feedback and support.</p>
                    <a href="{% url 'incubator:idea_create' %}" class="btn btn-primary fw-medium">Create Idea</a>"""

new_empty_btn = """                    {% if request.user == startup.founder %}
                    <p class="text-muted mb-4">Start drafting your first big idea to get feedback and support.</p>
                    <a href="{% url 'incubator:idea_create' %}" class="btn btn-primary fw-medium">Create Idea</a>
                    {% else %}
                    <p class="text-muted mb-4">The founder has not created any ideas yet.</p>
                    {% endif %}"""

if old_empty_btn in content:
    content = content.replace(old_empty_btn, new_empty_btn)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
