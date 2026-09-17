import os

file_path = 'dashboard/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the entire home view to correctly handle all roles and inject the required data.
# And add necessary imports.

new_imports = """
from incubator.models import Startup, Idea, Event, EventParticipation, CollaborationRequest, Notification, Activity, Document, Evaluation
from incubator.models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from core.models import User
"""

# We'll just replace the entire content for home view
old_home_def = """@login_required
def home(request):"""

# wait, it's safer to just rewrite dashboard/views.py entirely based on what I know.

new_dashboard_views = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserProfileForm
from incubator.views import get_active_startup
from django.utils import timezone
from core.models import User
from django.core.exceptions import PermissionDenied
from incubator.models import Startup, Idea, Event, EventParticipation, CollaborationRequest, Notification, Activity, Document, Evaluation
from incubator.models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from django.db.models import Sum

@login_required
def home(request):
    now = timezone.now()
    role = request.user.role
    
    if role == 'admin':
        context = {
            'total_users': User.objects.count(),
            'founders_count': User.objects.filter(role='founder').count(),
            'mentors_count': User.objects.filter(role='mentor').count(),
            'investors_count': User.objects.filter(role='investor').count(),
            'applicants_count': User.objects.filter(role='applicant').count(),
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
            
            # Batch 8 KPIs
            'total_rounds': FundingRound.objects.count(),
            'open_rounds': FundingRound.objects.filter(status='open').count(),
            'total_target': FundingRound.objects.aggregate(t=Sum('target_amount'))['t'] or 0,
            'total_raised': FundingRound.objects.aggregate(t=Sum('raised_amount'))['t'] or 0,
            'total_funding_apps': FundingApplication.objects.count(),
            'pending_funding_apps': FundingApplication.objects.filter(status='pending').count(),
            'total_meetings': InvestorMeeting.objects.count(),
            
            'total_jobs': JobPosting.objects.count(),
            'published_jobs': JobPosting.objects.filter(status='published').count(),
            'total_job_apps': JobApplication.objects.count(),
            'shortlisted_job_apps': JobApplication.objects.filter(status='shortlisted').count(),
            'total_interviews': Interview.objects.count(),
            
            'recent_activities': Activity.objects.all().order_by('-created_at')[:10],
            'recent_startups': Startup.objects.all().order_by('-created_at')[:5]
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
        
    elif role == 'mentor':
        mentored_startups = request.user.mentored_startups.all()
        from django.db.models import Case, When, IntegerField
        pending_ideas = Idea.objects.filter(
            startup__in=mentored_startups, 
            status__in=['submitted', 'under_review']
        ).annotate(
            priority=Case(
                When(status='submitted', then=1),
                When(status='under_review', then=2),
                output_field=IntegerField(),
            )
        ).order_by('priority', 'submitted_at')
        
        pending_reviews = pending_ideas.count()
        for s in mentored_startups:
            total_m = s.milestones.count()
            completed_m = s.milestones.filter(status='completed').count()
            s.progress_percentage = int((completed_m / total_m) * 100) if total_m > 0 else 0
            s.pending_ideas_count = s.ideas.filter(status__in=['submitted', 'under_review']).count()
        
        context = {
            'mentored_startups': mentored_startups,
            'pending_reviews': pending_reviews,
            'pending_ideas': pending_ideas,
            'upcoming_events': Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:3],
            'my_events': EventParticipation.objects.filter(participant=request.user, status='registered', event__start_datetime__gte=now).order_by('event__start_datetime')[:3],
            'pending_collabs': CollaborationRequest.objects.filter(recipient=request.user, status='pending').order_by('-created_at')[:3]
        }
        return render(request, 'dashboard/mentor_dashboard.html', context)

    elif role == 'investor':
        profile_exists = hasattr(request.user, 'investor_profile')
        open_rounds = FundingRound.objects.filter(status='open').order_by('-created_at')[:5]
        my_apps = FundingApplication.objects.filter(investor=request.user).order_by('-created_at')[:5]
        upcoming_meetings = InvestorMeeting.objects.filter(funding_application__investor=request.user, status='scheduled', scheduled_at__gte=now).order_by('scheduled_at')[:5]
        
        context = {
            'profile_exists': profile_exists,
            'open_rounds': open_rounds,
            'my_apps': my_apps,
            'upcoming_meetings': upcoming_meetings,
            'pending_collabs': CollaborationRequest.objects.filter(recipient=request.user, status='pending').order_by('-created_at')[:3]
        }
        return render(request, 'dashboard/investor_dashboard.html', context)

    elif role == 'applicant':
        my_apps = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')[:5]
        upcoming_interviews = Interview.objects.filter(application__applicant=request.user, status='scheduled', scheduled_at__gte=now).order_by('scheduled_at')[:5]
        
        context = {
            'my_apps': my_apps,
            'upcoming_interviews': upcoming_interviews,
        }
        return render(request, 'dashboard/applicant_dashboard.html', context)

    else:
        # Founder or Team Member
        startup = get_active_startup(request.user)
        ideas_count = 0
        submitted_ideas = 0
        under_review_ideas = 0
        team_members = 1
        progress_percentage = 0
        total_milestones = 0
        completed_milestones = 0
        activities = []
        
        my_events = EventParticipation.objects.filter(participant=request.user, status='registered', event__start_datetime__gte=now).order_by('event__start_datetime')[:3]
        upcoming_events = Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:3]
        
        pending_collabs = []
        sent_collabs = []
        
        # Funding & Hiring
        active_rounds = []
        pending_investor_apps = []
        upcoming_investor_meetings = []
        active_jobs = []
        pending_job_apps = []
        upcoming_interviews = []
        
        if startup:
            ideas_count = startup.ideas.count()
            submitted_ideas = startup.ideas.filter(status='submitted').count()
            under_review_ideas = startup.ideas.filter(status='under_review').count()
            total_milestones = startup.milestones.count()
            completed_milestones = startup.milestones.filter(status='completed').count()
            if total_milestones > 0:
                progress_percentage = int((completed_milestones / total_milestones) * 100)
            activities = startup.activities.all().order_by('-created_at')[:5]
            
            if request.user == startup.founder:
                pending_collabs = CollaborationRequest.objects.filter(recipient_startup=startup, status='pending').order_by('-created_at')[:3]
                sent_collabs = CollaborationRequest.objects.filter(requester_startup=startup, status='pending').order_by('-created_at')[:3]
                
                active_rounds = FundingRound.objects.filter(startup=startup, status='open')
                pending_investor_apps = FundingApplication.objects.filter(funding_round__startup=startup, status='pending')
                upcoming_investor_meetings = InvestorMeeting.objects.filter(funding_application__funding_round__startup=startup, status='scheduled', scheduled_at__gte=now)
                
                active_jobs = JobPosting.objects.filter(startup=startup, status='published')
                pending_job_apps = JobApplication.objects.filter(job__startup=startup, status__in=['submitted', 'reviewing'])
                upcoming_interviews = Interview.objects.filter(application__job__startup=startup, status='scheduled', scheduled_at__gte=now)

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
            'sent_collabs': sent_collabs,
            
            'active_rounds': active_rounds,
            'pending_investor_apps': pending_investor_apps,
            'upcoming_investor_meetings': upcoming_investor_meetings,
            'active_jobs': active_jobs,
            'pending_job_apps': pending_job_apps,
            'upcoming_interviews': upcoming_interviews,
        }
        return render(request, 'dashboard/home.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'dashboard/profile.html', {'form': form})

@login_required
def coming_soon_view(request, feature='feature'):
    feature_name = feature.replace('-', ' ').title()
    return render(request, 'dashboard/coming_soon.html', {'feature_name': feature_name, 'feature_slug': feature})

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

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_dashboard_views)
