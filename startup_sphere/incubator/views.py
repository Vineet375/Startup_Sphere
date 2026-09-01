from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from .models import Startup, Idea, Feedback, Milestone
from .forms import StartupForm, IdeaForm, FeedbackForm, MilestoneForm

@login_required
def startup_detail(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
        if request.user != startup.founder and request.user != startup.mentor and request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to view this startup.")
    else:
        try:
            startup = request.user.startup
        except Startup.DoesNotExist:
            messages.info(request, "You haven't registered a startup yet.")
            return redirect('incubator:register_startup')
            
    milestones = startup.milestones.all().order_by('target_date')
    return render(request, 'incubator/startup_detail.html', {'startup': startup, 'milestones': milestones})

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
    idea = get_object_or_404(Idea, id=idea_id)
    if request.user != idea.creator and request.user != idea.startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("You do not have permission to view this idea.")
        
    feedbacks = idea.feedbacks.all().order_by('-created_at')
    feedback_form = FeedbackForm() if request.user == idea.startup.mentor else None
    
    return render(request, 'incubator/idea_detail.html', {
        'idea': idea, 
        'feedbacks': feedbacks, 
        'feedback_form': feedback_form
    })

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

@login_required
def add_feedback(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.user != idea.startup.mentor:
        raise PermissionDenied("Only the assigned mentor can provide feedback.")
        
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.idea = idea
            feedback.mentor = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully.")
            
    return redirect('incubator:idea_detail', idea_id=idea.id)

@login_required
def mark_under_review(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.user != idea.startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("You do not have permission to change review status.")
        
    if request.method == 'POST' and idea.status == 'submitted':
        idea.status = 'under_review'
        idea.save()
        messages.success(request, "Idea status changed to Under Review.")
        
    return redirect('incubator:idea_detail', idea_id=idea.id)

@login_required
def milestone_create(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    if request.user != startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("Only the assigned mentor or an admin can create milestones.")
        
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.startup = startup
            milestone.save()
            messages.success(request, "Milestone created successfully.")
            return redirect('incubator:startup_detail_id', startup_id=startup.id) if request.user.role == 'mentor' else redirect('incubator:startup_detail')
    
    # Normally this would be a form page or modal, for now we will just use a basic template or fallback.
    # To keep it simple, we will assume this is handled via a dedicated template if needed.
    # For now, let's just render a form.
    form = MilestoneForm()
    return render(request, 'incubator/milestone_form.html', {'form': form, 'startup': startup})

@login_required
def milestone_update(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    startup = milestone.startup
    
    is_mentor_or_admin = (request.user == startup.mentor or request.user.role == 'admin')
    is_founder = (request.user == startup.founder)
    
    if not (is_mentor_or_admin or is_founder):
        raise PermissionDenied("You do not have permission to update this milestone.")
        
    if request.method == 'POST':
        if is_mentor_or_admin:
            form = MilestoneForm(request.POST, instance=milestone)
        else:
            # Founder can only update status
            form = MilestoneForm(instance=milestone)
            new_status = request.POST.get('status')
            if new_status in dict(Milestone.STATUS_CHOICES):
                milestone.status = new_status
                milestone.save()
                messages.success(request, "Milestone status updated.")
                return redirect('incubator:startup_detail')
                
        if form.is_valid() and is_mentor_or_admin:
            form.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('incubator:startup_detail_id', startup_id=startup.id) if request.user.role == 'mentor' else redirect('incubator:startup_detail')
            
    form = MilestoneForm(instance=milestone)
    if is_founder and not is_mentor_or_admin:
        # Founder can only see status dropdown
        for field_name in form.fields:
            if field_name != 'status':
                form.fields[field_name].disabled = True
                
    return render(request, 'incubator/milestone_form.html', {'form': form, 'startup': startup})

@login_required
def milestone_delete(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    startup = milestone.startup
    
    if request.user != startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("Only the assigned mentor or an admin can delete milestones.")
        
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, "Milestone deleted successfully.")
        
    return redirect('incubator:startup_detail_id', startup_id=startup.id) if request.user.role == 'mentor' else redirect('incubator:startup_detail')
