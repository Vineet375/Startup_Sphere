from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Startup, Idea
from .forms import StartupForm, IdeaForm

@login_required
def startup_detail(request):
    try:
        startup = request.user.startup
    except Startup.DoesNotExist:
        messages.info(request, "You haven't registered a startup yet.")
        return redirect('incubator:register_startup')
        
    return render(request, 'incubator/startup_detail.html', {'startup': startup})

@login_required
def register_startup(request):
    if hasattr(request.user, 'startup'):
        messages.info(request, "You have already registered a startup.")
        return redirect('incubator:startup_detail')
        
    if request.method == 'POST':
        form = StartupForm(request.POST, request.FILES)
        if form.is_valid():
            startup = form.save(commit=False)
            startup.founder = request.user
            startup.save()
            messages.success(request, "Your startup has been registered successfully!")
            return redirect('incubator:startup_detail')
    else:
        form = StartupForm()
        
    return render(request, 'incubator/startup_form.html', {'form': form, 'is_edit': False})

@login_required
def startup_edit(request):
    try:
        startup = request.user.startup
    except Startup.DoesNotExist:
        messages.error(request, "You do not have a startup to edit.")
        return redirect('incubator:register_startup')
        
    if request.method == 'POST':
        form = StartupForm(request.POST, request.FILES, instance=startup)
        if form.is_valid():
            form.save()
            messages.success(request, "Startup details updated successfully!")
            return redirect('incubator:startup_detail')
    else:
        form = StartupForm(instance=startup)
        
    return render(request, 'incubator/startup_form.html', {'form': form, 'is_edit': True})

@login_required
def idea_list(request):
    try:
        startup = request.user.startup
        ideas = startup.ideas.all().order_by('-updated_at')
    except Startup.DoesNotExist:
        messages.info(request, "You must register a startup before managing ideas.")
        return redirect('incubator:register_startup')
        
    return render(request, 'incubator/idea_list.html', {'ideas': ideas, 'startup': startup})

@login_required
def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, creator=request.user)
    return render(request, 'incubator/idea_detail.html', {'idea': idea})

@login_required
def idea_create(request):
    try:
        startup = request.user.startup
    except Startup.DoesNotExist:
        messages.error(request, "You must register a startup before creating an idea.")
        return redirect('incubator:register_startup')
        
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.startup = startup
            idea.creator = request.user
            
            if 'submit' in request.POST:
                idea.status = 'submitted'
                idea.submitted_at = timezone.now()
                messages.success(request, "Your idea has been submitted successfully!")
            else:
                idea.status = 'draft'
                messages.success(request, "Your idea has been saved as a draft.")
                
            idea.save()
            return redirect('incubator:idea_list')
    else:
        form = IdeaForm()
        
    return render(request, 'incubator/idea_form.html', {'form': form, 'is_edit': False})

@login_required
def idea_edit(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, creator=request.user)
    
    if idea.status != 'draft':
        messages.error(request, "You can only edit ideas that are in draft status.")
        return redirect('incubator:idea_detail', idea_id=idea.id)
        
    if request.method == 'POST':
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            idea = form.save(commit=False)
            
            if 'submit' in request.POST:
                idea.status = 'submitted'
                idea.submitted_at = timezone.now()
                messages.success(request, "Your idea has been submitted successfully!")
            else:
                messages.success(request, "Your draft has been updated.")
                
            idea.save()
            return redirect('incubator:idea_list')
    else:
        form = IdeaForm(instance=idea)
        
    return render(request, 'incubator/idea_form.html', {'form': form, 'is_edit': True})

@login_required
def idea_submit(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, creator=request.user)
    
    if idea.status != 'draft':
        messages.error(request, "This idea is already submitted.")
        return redirect('incubator:idea_detail', idea_id=idea.id)
        
    if request.method == 'POST':
        idea.status = 'submitted'
        idea.submitted_at = timezone.now()
        idea.save()
        messages.success(request, "Your idea has been submitted successfully!")
        return redirect('incubator:idea_list')
        
    return render(request, 'incubator/idea_submit_confirm.html', {'idea': idea})
