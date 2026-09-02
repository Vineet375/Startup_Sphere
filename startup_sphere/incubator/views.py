from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from .models import Startup, Idea, Feedback, Milestone, Activity, Notification
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
            Activity.objects.create(
                startup=startup,
                user=request.user,
                activity_type='startup_registered',
                description=f'Startup "{startup.name}" was registered.'
            )
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
                Activity.objects.create(
                    startup=startup,
                    user=request.user,
                    activity_type='idea_submitted',
                    description=f'Idea "{idea.title}" was submitted.'
                )
                if startup.mentor:
                    Notification.objects.create(
                        recipient=startup.mentor,
                        actor=request.user,
                        startup=startup,
                        title="Idea Submitted",
                        message=f"{startup.name} has submitted a new idea: {idea.title}.",
                        notification_type='idea_submitted',
                        link_url=reverse('incubator:idea_detail', args=[idea.id])
                    )
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
                Activity.objects.create(
                    startup=idea.startup,
                    user=request.user,
                    activity_type='idea_submitted',
                    description=f'Idea "{idea.title}" was submitted.'
                )
                if idea.startup.mentor:
                    Notification.objects.create(
                        recipient=idea.startup.mentor,
                        actor=request.user,
                        startup=idea.startup,
                        title="Idea Submitted",
                        message=f"{idea.startup.name} has submitted a new idea: {idea.title}.",
                        notification_type='idea_submitted',
                        link_url=reverse('incubator:idea_detail', args=[idea.id])
                    )
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
        Activity.objects.create(
            startup=idea.startup,
            user=request.user,
            activity_type='idea_submitted',
            description=f'Idea "{idea.title}" was submitted.'
        )
        if idea.startup.mentor:
            Notification.objects.create(
                recipient=idea.startup.mentor,
                actor=request.user,
                startup=idea.startup,
                title="Idea Submitted",
                message=f"{idea.startup.name} has submitted a new idea: {idea.title}.",
                notification_type='idea_submitted',
                link_url=reverse('incubator:idea_detail', args=[idea.id])
            )
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
            Activity.objects.create(
                startup=idea.startup,
                user=request.user,
                activity_type='feedback_added',
                description=f'Mentor provided feedback on "{idea.title}".'
            )
            Notification.objects.create(
                recipient=idea.startup.founder,
                actor=request.user,
                startup=idea.startup,
                title="New Feedback Received",
                message=f"Mentor {request.user.get_full_name() or request.user.username} provided feedback on your idea: {idea.title}.",
                notification_type='feedback_received',
                link_url=reverse('incubator:idea_detail', args=[idea.id])
            )
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
        Activity.objects.create(
            startup=idea.startup,
            user=request.user,
            activity_type='idea_under_review',
            description=f'Mentor marked the idea "{idea.title}" as Under Review.'
        )
        Notification.objects.create(
            recipient=idea.startup.founder,
            actor=request.user,
            startup=idea.startup,
            title="Idea Under Review",
            message=f'Your idea "{idea.title}" is now under review.',
            notification_type='idea_under_review',
            link_url=reverse('incubator:idea_detail', args=[idea.id])
        )
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
            Activity.objects.create(
                startup=startup,
                user=request.user,
                activity_type='milestone_created',
                description=f'Milestone "{milestone.title}" was created.'
            )
            Notification.objects.create(
                recipient=startup.founder,
                actor=request.user,
                startup=startup,
                title="New Milestone Created",
                message=f'A new milestone "{milestone.title}" has been created for your startup.',
                notification_type='milestone_created',
                link_url=reverse('incubator:startup_detail')
            )
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
        old_status = milestone.status
        if is_mentor_or_admin:
            form = MilestoneForm(request.POST, instance=milestone)
        else:
            # Founder can only update status
            form = MilestoneForm(instance=milestone)
            new_status = request.POST.get('status')
            if new_status in dict(Milestone.STATUS_CHOICES):
                milestone.status = new_status
                milestone.save()
                if old_status != 'completed' and new_status == 'completed':
                    Activity.objects.create(
                        startup=startup, user=request.user, activity_type='milestone_completed',
                        description=f'Milestone "{milestone.title}" was completed.'
                    )
                    if startup.mentor:
                        Notification.objects.create(
                            recipient=startup.mentor,
                            actor=request.user,
                            startup=startup,
                            title="Milestone Completed",
                            message=f'Milestone "{milestone.title}" for {startup.name} was marked as completed.',
                            notification_type='milestone_completed',
                            link_url=reverse('incubator:startup_detail_id', args=[startup.id])
                        )
                elif old_status != new_status:
                    Activity.objects.create(
                        startup=startup, user=request.user, activity_type='milestone_updated',
                        description=f'Milestone "{milestone.title}" status changed to {dict(Milestone.STATUS_CHOICES).get(new_status, new_status)}.'
                    )
                messages.success(request, "Milestone status updated.")
                return redirect('incubator:startup_detail')
                
        if form.is_valid() and is_mentor_or_admin:
            milestone = form.save()
            if old_status != 'completed' and milestone.status == 'completed':
                Activity.objects.create(
                    startup=startup, user=request.user, activity_type='milestone_completed',
                    description=f'Milestone "{milestone.title}" was completed.'
                )
            else:
                Activity.objects.create(
                    startup=startup, user=request.user, activity_type='milestone_updated',
                    description=f'Milestone "{milestone.title}" was updated.'
                )
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


from django.views.decorators.http import require_POST

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'incubator/notification_list.html', {'notifications': notifications})

@login_required
@require_POST
def notification_mark_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # After marking as read, optionally redirect to the link URL if provided in the form POST (as a next parameter)
    # But for a simple AJAX or form submit, we might just redirect back to notifications page
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('incubator:notification_list')

@login_required
@require_POST
def notification_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('incubator:notification_list')


@login_required
def startup_update_status(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    if request.user != startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("Only the assigned mentor or an admin can update the incubation status.")
        
    if request.method == 'POST':
        new_status = request.POST.get('incubation_status')
        if new_status in dict(Startup.INCUBATION_CHOICES):
            startup.incubation_status = new_status
            startup.save()
            messages.success(request, "Startup incubation status updated.")
            
    return redirect('incubator:startup_detail_id', startup_id=startup.id)
