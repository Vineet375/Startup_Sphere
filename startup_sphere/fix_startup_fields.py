import os

# 1. Fix views.py
views_path = 'incubator/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

views_content = views_content.replace(
    "industry = request.GET.get('industry')",
    "category = request.GET.get('category')"
).replace(
    "status = request.GET.get('status')",
    "status = request.GET.get('status')" # keep status GET param name, but filter on incubation_status
).replace(
    "Q(industry__icontains=q)",
    "Q(category__icontains=q)"
).replace(
    "if industry:\n        startups = startups.filter(industry__icontains=industry)",
    "if category:\n        startups = startups.filter(category=category)"
).replace(
    "if status:\n        startups = startups.filter(status=status)",
    "if status:\n        startups = startups.filter(incubation_status=status)"
).replace(
    "'industry': industry",
    "'category': category"
)
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)

# 2. Fix directory html
dir_html_path = 'templates/incubator/startup_directory.html'
with open(dir_html_path, 'r', encoding='utf-8') as f:
    dir_content = f.read()

dir_content = dir_content.replace(
    """<div class="col-md-3">
                    <label class="form-label text-muted small fw-bold">Industry</label>
                    <input type="text" name="industry" class="form-control" placeholder="e.g. Fintech" value="{{ industry|default:'' }}">
                </div>""",
    """<div class="col-md-3">
                    <label class="form-label text-muted small fw-bold">Category</label>
                    <select name="category" class="form-select">
                        <option value="">Any Category</option>
                        <option value="tech" {% if category == 'tech' %}selected{% endif %}>Technology</option>
                        <option value="health" {% if category == 'health' %}selected{% endif %}>Healthcare</option>
                        <option value="finance" {% if category == 'finance' %}selected{% endif %}>FinTech</option>
                        <option value="edu" {% if category == 'edu' %}selected{% endif %}>EdTech</option>
                        <option value="ecommerce" {% if category == 'ecommerce' %}selected{% endif %}>E-Commerce</option>
                        <option value="other" {% if category == 'other' %}selected{% endif %}>Other</option>
                    </select>
                </div>"""
).replace(
    """<option value="incubating" {% if status == 'incubating' %}selected{% endif %}>Incubating</option>
                        <option value="graduated" {% if status == 'graduated' %}selected{% endif %}>Graduated</option>
                        <option value="dropped" {% if status == 'dropped' %}selected{% endif %}>Dropped</option>""",
    """<option value="idea_stage" {% if status == 'idea_stage' %}selected{% endif %}>Idea Stage</option>
                        <option value="under_review" {% if status == 'under_review' %}selected{% endif %}>Under Review</option>
                        <option value="incubating" {% if status == 'incubating' %}selected{% endif %}>Incubating</option>
                        <option value="active" {% if status == 'active' %}selected{% endif %}>Active</option>
                        <option value="completed" {% if status == 'completed' %}selected{% endif %}>Completed</option>"""
).replace(
    "{{ startup.industry|default:\"No Industry\" }}",
    "{{ startup.get_category_display|default:\"No Category\" }}"
).replace(
    "{{ startup.get_status_display }}",
    "{{ startup.get_incubation_status_display }}"
)
with open(dir_html_path, 'w', encoding='utf-8') as f:
    f.write(dir_content)

# 3. Fix profile html
profile_html_path = 'templates/incubator/startup_public_profile.html'
with open(profile_html_path, 'r', encoding='utf-8') as f:
    profile_content = f.read()

profile_content = profile_content.replace(
    "{{ startup.industry|default:\"Uncategorized\" }}",
    "{{ startup.get_category_display|default:\"Uncategorized\" }}"
).replace(
    "{{ startup.get_status_display }}",
    "{{ startup.get_incubation_status_display }}"
)
with open(profile_html_path, 'w', encoding='utf-8') as f:
    f.write(profile_content)

# 4. Fix tests.py
tests_path = 'incubator/tests.py'
with open(tests_path, 'r', encoding='utf-8') as f:
    tests_content = f.read()

tests_content = tests_content.replace(
    "industry='Fintech', status='incubating'",
    "category='finance', incubation_status='incubating'"
).replace(
    "industry='Healthtech', status='graduated'",
    "category='health', incubation_status='completed'"
).replace(
    "?industry=Healthtech",
    "?category=health"
)
with open(tests_path, 'w', encoding='utf-8') as f:
    f.write(tests_content)
