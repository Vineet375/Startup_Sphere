from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserProfileForm
from incubator.models import Startup, Idea
from incubator.views import get_active_startup

@login_required
def home(request):
    if request.user.role == 'mentor':
        mentored_startups = request.user.mentored_startups.all()
        # Find ideas for mentored startups that are submitted or under review
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
        
        # Calculate stats for each startup
        for s in mentored_startups:
            total_m = s.milestones.count()
            completed_m = s.milestones.filter(status='completed').count()
            s.progress_percentage = int((completed_m / total_m) * 100) if total_m > 0 else 0
            s.pending_ideas_count = s.ideas.filter(status__in=['submitted', 'under_review']).count()
        
        context = {
            'mentored_startups': mentored_startups,
            'pending_reviews': pending_reviews,
            'pending_ideas': pending_ideas,
        }
        return render(request, 'dashboard/mentor_dashboard.html', context)
        
    startup = None
    ideas_count = 0
    submitted_ideas = 0
    under_review_ideas = 0
    team_members = 1 # Just the founder for now
    progress_percentage = 0
    total_milestones = 0
    completed_milestones = 0
    activities = []
    
    startup = get_active_startup(request.user)
    if startup:
        ideas_count = startup.ideas.count()
        submitted_ideas = startup.ideas.filter(status='submitted').count()
        under_review_ideas = startup.ideas.filter(status='under_review').count()
        
        total_milestones = startup.milestones.count()
        completed_milestones = startup.milestones.filter(status='completed').count()
        if total_milestones > 0:
            progress_percentage = int((completed_milestones / total_milestones) * 100)
            
        activities = startup.activities.all().order_by('-created_at')[:5]
        
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
