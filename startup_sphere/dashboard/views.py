from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserProfileForm

@login_required
def home(request):
    return render(request, 'dashboard/home.html')

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
