import os

# HOME HTML (Founder/Team)
home_path = 'templates/dashboard/home.html'
with open(home_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

events_collabs_html = """
    <div class="row mt-4">
        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                    <h6 class="fw-bold mb-0">Upcoming Events</h6>
                    <a href="{% url 'incubator:event_list' %}" class="text-decoration-none small">View All</a>
                </div>
                <div class="card-body">
                    {% if upcoming_events %}
                        <div class="list-group list-group-flush">
                            {% for event in upcoming_events %}
                                <a href="{% url 'incubator:event_detail' event.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                    <div class="d-flex justify-content-between w-100">
                                        <h6 class="mb-1 text-truncate" style="max-width: 75%;">{{ event.title }}</h6>
                                        <small class="text-muted">{{ event.start_datetime|date:"M d" }}</small>
                                    </div>
                                    <small class="text-muted d-block text-truncate">{{ event.get_event_type_display }} • {{ event.venue|default:"Online" }}</small>
                                </a>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted small mb-0 mt-2">No upcoming events right now.</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between align-items-center">
                    <h6 class="fw-bold mb-0">Collaboration Requests</h6>
                    <a href="{% url 'incubator:collaboration_list' %}" class="text-decoration-none small">View All</a>
                </div>
                <div class="card-body">
                    {% if pending_collabs %}
                        <div class="list-group list-group-flush">
                            {% for collab in pending_collabs %}
                                <a href="{% url 'incubator:collaboration_detail' collab.id %}" class="list-group-item list-group-item-action px-0 border-bottom">
                                    <div class="d-flex justify-content-between w-100">
                                        <h6 class="mb-1 text-truncate" style="max-width: 75%;">{{ collab.title }}</h6>
                                        <small class="text-warning fw-medium">Pending</small>
                                    </div>
                                    <small class="text-muted d-block text-truncate">From: {{ collab.requester.username }}</small>
                                </a>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted small mb-0 mt-2">No pending requests.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
"""

# Append just before the final </div> or main block ends.
if "Upcoming Events" not in home_content:
    # insert before endblock
    home_content = home_content.replace("{% endblock layout %}", events_collabs_html + "\n{% endblock layout %}")
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(home_content)

# MENTOR DASHBOARD
mentor_path = 'templates/dashboard/mentor_dashboard.html'
with open(mentor_path, 'r', encoding='utf-8') as f:
    mentor_content = f.read()

if "Upcoming Events" not in mentor_content:
    mentor_content = mentor_content.replace("{% endblock layout %}", events_collabs_html + "\n{% endblock layout %}")
    with open(mentor_path, 'w', encoding='utf-8') as f:
        f.write(mentor_content)
