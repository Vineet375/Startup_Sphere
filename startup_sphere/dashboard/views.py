from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserProfileForm
from incubator.models import Startup, Idea

@login_required
def home(request):
    startup = None
    ideas_count = 0
    submitted_ideas = 0
    team_members = 1 # Just the founder for now
    
    if hasattr(request.user, 'startup'):
        startup = request.user.startup
        ideas_count = startup.ideas.count()
        submitted_ideas = startup.ideas.exclude(status='draft').count()
        
    context = {
        'startup': startup,
        'ideas_count': ideas_count,
        'submitted_ideas': submitted_ideas,
        'team_members': team_members,
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
