from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StartupRegistrationForm

@login_required
def register_startup(request):
    if hasattr(request.user, 'startup'):
        messages.info(request, "You have already registered a startup.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = StartupRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            startup = form.save(commit=False)
            startup.founder = request.user
            startup.save()
            messages.success(request, "Your startup has been registered successfully!")
            return redirect('dashboard:home')
    else:
        form = StartupRegistrationForm()
        
    return render(request, 'incubator/register_startup.html', {'form': form})
