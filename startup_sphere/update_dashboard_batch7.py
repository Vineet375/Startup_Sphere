import os

file_path = 'dashboard/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update imports
old_imports = """from django.contrib import messages
from accounts.forms import UserProfileForm
from incubator.models import Startup, Idea
from incubator.views import get_active_startup"""

new_imports = """from django.contrib import messages
from accounts.forms import UserProfileForm
from incubator.models import Startup, Idea, Event, EventParticipation, CollaborationRequest, Notification, Activity, Document, Evaluation
from incubator.views import get_active_startup
from django.utils import timezone
from core.models import User
from django.core.exceptions import PermissionDenied"""

content = content.replace(old_imports, new_imports)

# Update home view to handle admin and add events/collaborations
old_home = """@login_required
def home(request):
    if request.user.role == 'mentor':"""

new_home = """@login_required
def home(request):
    now = timezone.now()
    
    if request.user.role == 'admin':
        # Admin Dashboard KPIs
        context = {
            'total_users': User.objects.count(),
            'founders_count': User.objects.filter(role='founder').count(),
            'mentors_count': User.objects.filter(role='mentor').count(),
            'investors_count': User.objects.filter(role='investor').count(),
            'total_startups': Startup.objects.count(),
            'active_startups': Startup.objects.filter(incubation_status__in=['active', 'graduated']).count(),
            'total_ideas': Idea.objects.count(),
            'pending_ideas': Idea.objects.filter(status='submitted').count(),
            'total_events': Event.objects.count(),
            'upcoming_events': Event.objects.filter(start_datetime__gte=now).count(),
            'total_collabs': CollaborationRequest.objects.count(),
            'pending_collabs': CollaborationRequest.objects.filter(status='pending').count(),
            'total_evals': Evaluation.objects.count(),
            'total_docs': Document.objects.count(),
            'recent_activities': Activity.objects.all().order_by('-created_at')[:10],
            'recent_startups': Startup.objects.all().order_by('-created_at')[:5]
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
        
    if request.user.role == 'mentor':"""

content = content.replace(old_home, new_home)

# Add event/collab queries to mentor
old_mentor_context = """        context = {
            'mentored_startups': mentored_startups,
            'pending_reviews': pending_reviews,
            'pending_ideas': pending_ideas,
        }"""

new_mentor_context = """        context = {
            'mentored_startups': mentored_startups,
            'pending_reviews': pending_reviews,
            'pending_ideas': pending_ideas,
            'upcoming_events': Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:3],
            'my_events': EventParticipation.objects.filter(participant=request.user, status='registered', event__start_datetime__gte=now).order_by('event__start_datetime')[:3],
            'pending_collabs': CollaborationRequest.objects.filter(recipient=request.user, status='pending').order_by('-created_at')[:3]
        }"""

content = content.replace(old_mentor_context, new_mentor_context)

# Add event/collab queries to founder
old_founder_context = """    context = {
        'startup': startup,
        'ideas_count': ideas_count,
        'submitted_ideas': submitted_ideas,
        'under_review_ideas': under_review_ideas,
        'team_members': team_members,
        'progress_percentage': progress_percentage,
        'total_milestones': total_milestones,
        'completed_milestones': completed_milestones,
        'activities': activities,
    }"""

new_founder_context = """    my_events = EventParticipation.objects.filter(participant=request.user, status='registered', event__start_datetime__gte=now).order_by('event__start_datetime')[:3]
    upcoming_events = Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:3]
    
    pending_collabs = []
    sent_collabs = []
    if startup and request.user == startup.founder:
        pending_collabs = CollaborationRequest.objects.filter(recipient_startup=startup, status='pending').order_by('-created_at')[:3]
        sent_collabs = CollaborationRequest.objects.filter(requester_startup=startup, status='pending').order_by('-created_at')[:3]

    context = {
        'startup': startup,
        'ideas_count': ideas_count,
        'submitted_ideas': submitted_ideas,
        'under_review_ideas': under_review_ideas,
        'team_members': team_members,
        'progress_percentage': progress_percentage,
        'total_milestones': total_milestones,
        'completed_milestones': completed_milestones,
        'activities': activities,
        'upcoming_events': upcoming_events,
        'my_events': my_events,
        'pending_collabs': pending_collabs,
        'sent_collabs': sent_collabs
    }"""

content = content.replace(old_founder_context, new_founder_context)

# Now define all the admin views
admin_views = """

# ----------------- ADMIN VIEWS -----------------

@login_required
def admin_users(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/admin_users.html', {'users': users})

@login_required
def admin_startups(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    startups = Startup.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_startups.html', {'startups': startups})

@login_required
def admin_ideas(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    ideas = Idea.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_ideas.html', {'ideas': ideas})

@login_required
def admin_events(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    events = Event.objects.all().order_by('-start_datetime')
    return render(request, 'dashboard/admin_events.html', {'events': events})

@login_required
def admin_collaborations(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    collabs = CollaborationRequest.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_collabs.html', {'collabs': collabs})

@login_required
def admin_activities(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    activities = Activity.objects.all().order_by('-created_at')[:200]
    return render(request, 'dashboard/admin_activities.html', {'activities': activities})
"""

content += admin_views

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
