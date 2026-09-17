from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from .models import Startup, Idea, Feedback, Milestone, Activity, Notification
from .forms import StartupForm, IdeaForm, FeedbackForm, MilestoneForm


from .models import TeamMember, Document
from .forms import TeamMemberInviteForm, TeamMemberUpdateForm, DocumentForm

def get_active_startup(user):
    if hasattr(user, 'startup'):
        return user.startup
    team_member = user.startup_teams.filter(status='active').first()
    if team_member:
        return team_member.startup
    return None

def is_active_team_member(user, startup):
    return TeamMember.objects.filter(startup=startup, user=user, status='active').exists()

@login_required
def startup_detail(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
        is_founder = request.user == startup.founder
        is_mentor = request.user == startup.mentor
        is_admin = request.user.role == 'admin'
        is_team = is_active_team_member(request.user, startup)
        if not (is_founder or is_mentor or is_admin or is_team):
            raise PermissionDenied("You do not have permission to view this startup.")
    else:
        startup = get_active_startup(request.user)
        if not startup:
            messages.info(request, "You haven't registered a startup yet.")
            return redirect('incubator:register_startup')
        
        is_founder = request.user == startup.founder
        is_mentor = request.user == startup.mentor
        is_admin = request.user.role == 'admin'
        is_team = is_active_team_member(request.user, startup)
            
    milestones = startup.milestones.all().order_by('target_date')
    return render(request, 'incubator/startup_detail.html', {
        'startup': startup, 
        'milestones': milestones,
        'is_founder': is_founder,
        'is_mentor': is_mentor,
        'is_admin': is_admin,
        'is_team': is_team
    })

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
    startup = get_active_startup(request.user)
    if not startup:
        if request.user.role == 'founder':
            messages.info(request, "You must register a startup before managing ideas.")
            return redirect('incubator:register_startup')
        else:
            messages.error(request, "You are not associated with any startup.")
            return redirect('dashboard:home')
            
    ideas = startup.ideas.all().order_by('-updated_at')
        
    return render(request, 'incubator/idea_list.html', {'ideas': ideas, 'startup': startup})

@login_required
def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    startup = idea.startup
    is_founder = request.user == startup.founder
    is_mentor = request.user == startup.mentor
    is_admin = request.user.role == 'admin'
    is_team = is_active_team_member(request.user, startup)
    if not (is_founder or is_mentor or is_admin or is_team):
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


@login_required
def team_list(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
        if request.user != startup.mentor and request.user.role != 'admin':
            raise PermissionDenied("Only the assigned mentor or an admin can view this startup's team via this URL.")
    else:
        startup = get_active_startup(request.user)
        if not startup:
            messages.info(request, "You must register a startup before managing a team.")
            return redirect('incubator:register_startup')
        
    team_members = startup.team_members.all().order_by('status', '-created_at')
    return render(request, 'incubator/team_list.html', {'startup': startup, 'team_members': team_members})

@login_required
def team_invite(request):
    startup = get_active_startup(request.user)
    if not startup or request.user != startup.founder:
        raise PermissionDenied("Only the founder can invite team members.")
        
    if request.method == 'POST':
        form = TeamMemberInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check duplicate
            if startup.founder.email == email:
                messages.error(request, "You cannot invite yourself.")
                return redirect('incubator:team_list')
                
            from django.contrib.auth import get_user_model
            User = get_user_model()
            existing_user = User.objects.filter(email=email).first()
            
            if existing_user:
                if TeamMember.objects.filter(startup=startup, user=existing_user).exists():
                    messages.error(request, "This user is already on the team.")
                    return redirect('incubator:team_list')
            else:
                if TeamMember.objects.filter(startup=startup, invited_email=email).exists():
                    messages.error(request, "This email has already been invited.")
                    return redirect('incubator:team_list')

            team_member = form.save(commit=False)
            team_member.startup = startup
            
            if existing_user:
                team_member.user = existing_user
                team_member.status = 'active'
                team_member.joined_at = timezone.now()
                team_member.save()
                Activity.objects.create(startup=startup, user=request.user, activity_type='team_member_added', description=f'User {existing_user.username} was added to the team.')
                Notification.objects.create(
                    recipient=existing_user,
                    actor=request.user,
                    startup=startup,
                    title="Added to Startup Team",
                    message=f"You have been added to the team for {startup.name}.",
                    notification_type='team_member_added',
                    link_url=reverse('incubator:team_list')
                )
                messages.success(request, f"User {existing_user.username} successfully added to the team.")
            else:
                team_member.invited_email = email
                team_member.status = 'pending'
                team_member.save()
                Activity.objects.create(startup=startup, user=request.user, activity_type='pending_invitation_created', description=f'Pending invitation created for {email}.')
                messages.success(request, f"Invitation sent to {email}.")
                
            return redirect('incubator:team_list')
    else:
        form = TeamMemberInviteForm()
        
    return render(request, 'incubator/team_invite.html', {'form': form})

@login_required
@require_POST
def team_remove(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    startup = team_member.startup
    if request.user != startup.founder:
        raise PermissionDenied("Only the founder can remove team members.")
        
    team_member.delete()
    Activity.objects.create(startup=startup, user=request.user, activity_type='team_member_removed', description=f'Team member was removed.')
    messages.success(request, "Team member removed.")
    return redirect('incubator:team_list')

@login_required
def document_list(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
        if request.user != startup.mentor and request.user.role != 'admin':
            raise PermissionDenied("Only the assigned mentor or an admin can view this startup's documents via this URL.")
    else:
        startup = get_active_startup(request.user)
        if not startup:
            messages.info(request, "You must register a startup before managing documents.")
            return redirect('incubator:register_startup')
            
    category = request.GET.get('category')
    documents = startup.documents.all().order_by('-created_at')
    if category:
        documents = documents.filter(category=category)
        
    return render(request, 'incubator/document_list.html', {'startup': startup, 'documents': documents, 'current_category': category})

@login_required
def document_upload(request):
    startup = get_active_startup(request.user)
    if not startup or request.user != startup.founder:
        raise PermissionDenied("Only the founder can upload documents.")
        
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.startup = startup
            document.uploaded_by = request.user
            document.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='document_uploaded', description=f'Document "{document.title}" was uploaded.')
            messages.success(request, "Document uploaded successfully.")
            return redirect('incubator:document_list')
    else:
        form = DocumentForm()
        
    return render(request, 'incubator/document_form.html', {'form': form})

@login_required
@require_POST
def document_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    startup = document.startup
    if request.user != startup.founder:
        raise PermissionDenied("Only the founder can delete documents.")
        
    title = document.title
    document.file.delete()
    document.delete()
    Activity.objects.create(startup=startup, user=request.user, activity_type='document_deleted', description=f'Document "{title}" was deleted.')
    messages.success(request, "Document deleted successfully.")
    return redirect('incubator:document_list')

@login_required
def team_member_edit(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    startup = team_member.startup
    if request.user != startup.founder:
        raise PermissionDenied("Only the founder can edit team members.")
        
    if request.method == 'POST':
        form = TeamMemberUpdateForm(request.POST, instance=team_member)
        if form.is_valid():
            form.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='team_member_updated', description=f"Team member position updated.")
            messages.success(request, "Team member updated successfully.")
            return redirect('incubator:team_list')
    else:
        form = TeamMemberUpdateForm(instance=team_member)
        
    return render(request, 'incubator/team_member_edit.html', {'form': form, 'team_member': team_member})

@login_required
def document_edit(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    startup = document.startup
    if request.user != startup.founder:
        raise PermissionDenied("Only the founder can edit documents.")
        
    if request.method == 'POST':
        # We only update metadata, not the file itself in this simple edit
        # To allow file update, we would pass request.FILES and use DocumentForm
        # But wait, DocumentForm requires 'file', so we can use a subset or just use DocumentForm and make file not required for edit
        # Let's check DocumentForm. 
        form = DocumentForm(request.POST, request.FILES, instance=document)
        # file is required by default in ModelForm if it's required in model. We can make it optional for edits by tweaking the form instance or just defining a specific form.
        # But wait, FileField is blank=False by default. We can bypass by making the field required=False dynamically.
        form.fields['file'].required = False
        
        if form.is_valid():
            form.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='document_updated', description=f'Document "{document.title}" was updated.')
            messages.success(request, "Document updated successfully.")
            return redirect('incubator:document_list')
    else:
        form = DocumentForm(instance=document)
        form.fields['file'].required = False
        
    return render(request, 'incubator/document_edit.html', {'form': form, 'document': document})

from django.db.models import Q
from core.models import User
from .models import Evaluation
from .forms import EvaluationForm

@login_required
def startup_directory(request):
    startups = Startup.objects.all().order_by('-created_at')
    
    q = request.GET.get('q')
    category = request.GET.get('category')
    status = request.GET.get('status')
    
    if q:
        startups = startups.filter(
            Q(name__icontains=q) | 
            Q(tagline__icontains=q) | 
            Q(category__icontains=q)
        )
    if category:
        startups = startups.filter(category=category)
    if status:
        startups = startups.filter(incubation_status=status)
        
    return render(request, 'incubator/startup_directory.html', {
        'startups': startups,
        'q': q,
        'category': category,
        'status': status
    })

@login_required
def startup_public_profile(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    return render(request, 'incubator/startup_public_profile.html', {'startup': startup})

@login_required
def evaluation_list(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    # Permissions
    is_founder = (request.user == startup.founder)
    is_assigned_mentor = (request.user == startup.mentor)
    is_admin = request.user.role == 'admin'
    is_active_team_member = startup.team_members.filter(user=request.user, status='active').exists()
    
    if not (is_founder or is_assigned_mentor or is_admin or is_active_team_member):
        raise PermissionDenied("You do not have permission to view this startup's evaluations.")
        
    evaluations = startup.evaluations.all().order_by('-updated_at')
    
    user_evaluation = None
    if is_assigned_mentor:
        user_evaluation = evaluations.filter(evaluator=request.user).first()
        
    from django.db.models import Avg
    avg_overall = evaluations.aggregate(Avg('overall_score'))['overall_score__avg']
    
    return render(request, 'incubator/evaluation_list.html', {
        'startup': startup,
        'evaluations': evaluations,
        'user_evaluation': user_evaluation,
        'avg_overall': avg_overall,
        'is_founder': is_founder,
        'is_assigned_mentor': is_assigned_mentor,
    })

@login_required
def evaluation_create(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    # Permissions
    if request.user != startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("Only the assigned mentor or an admin can evaluate this startup.")
        
    if Evaluation.objects.filter(startup=startup, evaluator=request.user).exists():
        messages.error(request, "You have already evaluated this startup. You can edit your existing evaluation.")
        return redirect('incubator:evaluation_list', startup_id=startup.id)
        
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.startup = startup
            evaluation.evaluator = request.user
            evaluation.save()
            
            Activity.objects.create(
                startup=startup, 
                user=request.user, 
                activity_type='evaluation_created', 
                description=f'Evaluation submitted with overall score: {evaluation.overall_score:.1f}'
            )
            
            Notification.objects.create(
                recipient=startup.founder,
                actor=request.user,
                startup=startup,
                title='New Startup Evaluation',
                message=f'Your startup has received a new evaluation from {request.user.get_full_name() or request.user.username}.',
                notification_type='evaluation_received',
                link_url=reverse('incubator:evaluation_list', args=[startup.id])
            )
            
            messages.success(request, "Evaluation submitted successfully.")
            return redirect('incubator:evaluation_list', startup_id=startup.id)
    else:
        form = EvaluationForm()
        
    return render(request, 'incubator/evaluation_form.html', {'form': form, 'startup': startup})

@login_required
def evaluation_edit(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    startup = evaluation.startup
    
    if request.user != evaluation.evaluator and request.user.role != 'admin':
        raise PermissionDenied("You can only edit your own evaluations.")
        
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            evaluation = form.save()
            
            Activity.objects.create(
                startup=startup, 
                user=request.user, 
                activity_type='evaluation_updated', 
                description=f'Evaluation updated. New overall score: {evaluation.overall_score:.1f}'
            )
            
            messages.success(request, "Evaluation updated successfully.")
            return redirect('incubator:evaluation_list', startup_id=startup.id)
    else:
        form = EvaluationForm(instance=evaluation)
        
    return render(request, 'incubator/evaluation_form.html', {'form': form, 'startup': startup, 'evaluation': evaluation})

from django.db.models import Q
from core.models import User
from django.utils import timezone
from .models import Event, EventParticipation, CollaborationRequest
from .forms import EventForm, CollaborationRequestForm

# ----------------- EVENTS MODULE -----------------

@login_required
def event_list(request):
    now = timezone.now()
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'upcoming')
    
    events = Event.objects.all().order_by('start_datetime')
    
    if status_filter:
        events = events.filter(status=status_filter)
        
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    registered_event_ids = []
    if request.user.is_authenticated:
        registered_event_ids = EventParticipation.objects.filter(participant=request.user, status='registered').values_list('event_id', flat=True)
        
    return render(request, 'incubator/event_list.html', {
        'events': events,
        'registered_event_ids': registered_event_ids,
        'query': query,
        'status_filter': status_filter,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = EventParticipation.objects.filter(event=event, participant=request.user).first()
    
    # Check if full
    current_participants = event.participations.filter(status='registered').count()
    is_full = event.capacity is not None and current_participants >= event.capacity
    
    return render(request, 'incubator/event_detail.html', {
        'event': event,
        'participation': participation,
        'is_full': is_full,
        'current_participants': current_participants
    })

@login_required
def event_create(request):
    if request.user.role not in ['admin', 'mentor']:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('incubator:event_list')
    else:
        form = EventForm()
        
    return render(request, 'incubator/event_form.html', {'form': form, 'title': 'Create Event'})

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('incubator:event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
        
    return render(request, 'incubator/event_form.html', {'form': form, 'title': 'Edit Event'})

@login_required
def event_cancel(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        event.status = 'cancelled'
        event.save()
        
        # Notify participants
        for p in event.participations.filter(status='registered'):
            Notification.objects.create(
                recipient=p.participant,
                title=f"Event Cancelled: {event.title}",
                message=f"The event {event.title} has been cancelled.",
                notification_type='event_cancelled_notify'
            )
            
        messages.success(request, 'Event cancelled successfully!')
        return redirect('incubator:event_detail', event_id=event.id)
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_register(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.status != 'upcoming':
        messages.error(request, 'You can only register for upcoming events.')
        return redirect('incubator:event_detail', event_id=event.id)
        
    current_participants = event.participations.filter(status='registered').count()
    if event.capacity and current_participants >= event.capacity:
        messages.error(request, 'This event is already full.')
        return redirect('incubator:event_detail', event_id=event.id)
        
    participation, created = EventParticipation.objects.get_or_create(
        event=event,
        participant=request.user,
        defaults={'status': 'registered'}
    )
    
    if not created:
        if participation.status == 'cancelled':
            participation.status = 'registered'
            participation.save()
            messages.success(request, 'Re-registered for event.')
        else:
            messages.info(request, 'You are already registered for this event.')
    else:
        Notification.objects.create(
            recipient=request.user,
            title="Event Registration Successful",
            message=f"You have registered for {event.title}.",
            notification_type='event_registered',
            link_url=f"/incubator/events/{event.id}/"
        )
        messages.success(request, 'Successfully registered for event!')
        
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_unregister(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = get_object_or_404(EventParticipation, event=event, participant=request.user)
    
    if request.method == 'POST':
        participation.status = 'cancelled'
        participation.save()
        messages.success(request, 'Your registration has been cancelled.')
        
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    participants = event.participations.all().order_by('-registered_at')
    return render(request, 'incubator/event_participants.html', {'event': event, 'participants': participants})

@login_required
def event_mark_attendance(request, event_id, participation_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    participation = get_object_or_404(EventParticipation, id=participation_id, event=event)
    if request.method == 'POST':
        participation.status = 'attended'
        participation.attended_at = timezone.now()
        participation.save()
        messages.success(request, 'Attendance marked successfully.')
        
    return redirect('incubator:event_participants', event_id=event.id)


# ----------------- COLLABORATION MODULE -----------------

@login_required
def collaboration_directory(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id).order_by('username')
    
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        
    return render(request, 'incubator/collaboration_directory.html', {'users': users, 'query': query})

@login_required
def collaboration_request_create(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if recipient == request.user:
        messages.error(request, "You cannot send a collaboration request to yourself.")
        return redirect('incubator:collaboration_directory')
        
    requester_startup = get_active_startup(request.user)
    recipient_startup = get_active_startup(recipient)
    
    if requester_startup and recipient_startup and requester_startup == recipient_startup:
        messages.error(request, "You cannot send a collaboration request to someone in your own startup.")
        return redirect('incubator:collaboration_directory')
        
    # Check duplicate
    existing = CollaborationRequest.objects.filter(requester=request.user, recipient=recipient, status='pending').exists()
    if existing:
        messages.warning(request, "You already have a pending request with this user.")
        return redirect('incubator:collaboration_directory')

    if request.method == 'POST':
        form = CollaborationRequestForm(request.POST)
        if form.is_valid():
            collab = form.save(commit=False)
            collab.requester = request.user
            collab.recipient = recipient
            collab.requester_startup = requester_startup
            collab.recipient_startup = recipient_startup
            collab.save()
            
            Notification.objects.create(
                recipient=recipient,
                actor=request.user,
                title="New Collaboration Request",
                message=f"You received a collaboration request from {request.user.get_full_name() or request.user.username}.",
                notification_type='collaboration_received',
                link_url=reverse('incubator:collaboration_detail', args=[collab.id])
            )
            messages.success(request, 'Collaboration request sent successfully.')
            return redirect('incubator:collaboration_list')
    else:
        form = CollaborationRequestForm()
        
    return render(request, 'incubator/collaboration_form.html', {'form': form, 'recipient': recipient})

@login_required
def collaboration_list(request):
    sent_requests = CollaborationRequest.objects.filter(requester=request.user).order_by('-created_at')
    received_requests = CollaborationRequest.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'incubator/collaboration_list.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

@login_required
def collaboration_detail(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user not in [collab.requester, collab.recipient] and request.user.role != 'admin':
        raise PermissionDenied
        
    return render(request, 'incubator/collaboration_detail.html', {'collab': collab})

@login_required
def collaboration_accept(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.recipient:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'accepted'
        collab.responded_at = timezone.now()
        collab.save()
        
        Notification.objects.create(
            recipient=collab.requester,
            actor=request.user,
            title="Collaboration Request Accepted",
            message=f"{request.user.username} accepted your request.",
            notification_type='collaboration_accepted',
            link_url=reverse('incubator:collaboration_detail', args=[collab.id])
        )
        messages.success(request, 'Request accepted.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)

@login_required
def collaboration_reject(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.recipient:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'rejected'
        collab.responded_at = timezone.now()
        collab.save()
        
        Notification.objects.create(
            recipient=collab.requester,
            actor=request.user,
            title="Collaboration Request Rejected",
            message=f"{request.user.username} declined your request.",
            notification_type='collaboration_rejected',
            link_url=reverse('incubator:collaboration_detail', args=[collab.id])
        )
        messages.success(request, 'Request rejected.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)

@login_required
def collaboration_cancel(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.requester:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'cancelled'
        collab.save()
        messages.success(request, 'Request cancelled.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)


from .models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from .forms import InvestorProfileForm, FundingRoundForm, FundingApplicationForm, InvestorMeetingForm, JobPostingForm, JobApplicationForm, InterviewForm
from django.db.models import Sum

# ----------------- INVESTOR PROFILES -----------------

@login_required
def investor_profile_edit(request):
    if request.user.role != 'investor':
        raise PermissionDenied

    profile, created = InvestorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Investor profile updated successfully.')
            return redirect('incubator:investor_profile_detail', user_id=request.user.id)
    else:
        form = InvestorProfileForm(instance=profile)
    return render(request, 'incubator/investor_profile_form.html', {'form': form})

@login_required
def investor_profile_detail(request, user_id):
    investor_user = get_object_or_404(User, id=user_id, role='investor')
    profile = get_object_or_404(InvestorProfile, user=investor_user)
    return render(request, 'incubator/investor_profile_detail.html', {'profile': profile})

@login_required
def investor_directory(request):
    query = request.GET.get('q', '')
    investor_type = request.GET.get('investor_type', '')
    
    profiles = InvestorProfile.objects.select_related('user').all().order_by('-created_at')
    
    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(organization_name__icontains=query) |
            Q(investment_focus__icontains=query)
        )
    if investor_type:
        profiles = profiles.filter(investor_type=investor_type)
        
    return render(request, 'incubator/investor_directory.html', {'profiles': profiles, 'query': query, 'investor_type': investor_type})


# ----------------- FUNDING ROUNDS -----------------

@login_required
def funding_round_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        if not startup:
            messages.warning(request, "Register a startup first.")
            return redirect('dashboard:home')
        rounds = FundingRound.objects.filter(startup=startup).order_by('-created_at')
        is_founder = True
    else:
        # Investor view: open rounds
        rounds = FundingRound.objects.filter(status='open').order_by('-created_at')
        is_founder = False
        
    return render(request, 'incubator/funding_round_list.html', {'rounds': rounds, 'is_founder': is_founder})

@login_required
def funding_round_detail(request, round_id):
    funding_round = get_object_or_404(FundingRound, id=round_id)
    startup = funding_round.startup
    
    is_owner = (request.user.role == 'founder' and startup.founder == request.user)
    has_access = is_owner or request.user.role in ['admin', 'investor']
    
    if request.user.role == 'mentor':
        has_access = startup in request.user.mentored_startups.all()
    if request.user.role == 'team_member':
        has_access = startup == get_active_startup(request.user)
        
    if not has_access:
        raise PermissionDenied
        
    applications = []
    has_applied = False
    my_application = None
    
    if is_owner or request.user.role == 'admin':
        applications = funding_round.applications.all().order_by('-created_at')
    elif request.user.role == 'investor':
        my_application = funding_round.applications.filter(investor=request.user).first()
        if my_application:
            has_applied = True
            
    return render(request, 'incubator/funding_round_detail.html', {
        'round': funding_round,
        'applications': applications,
        'is_owner': is_owner,
        'has_applied': has_applied,
        'my_application': my_application
    })

@login_required
def funding_round_create(request):
    if request.user.role != 'founder':
        raise PermissionDenied
    startup = get_active_startup(request.user)
    if not startup or startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = FundingRoundForm(request.POST)
        if form.is_valid():
            rnd = form.save(commit=False)
            rnd.startup = startup
            rnd.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='funding_round_created', description=f"Funding round {rnd.round_name} created.")
            messages.success(request, 'Funding round created.')
            return redirect('incubator:funding_round_list')
    else:
        form = FundingRoundForm()
    return render(request, 'incubator/funding_round_form.html', {'form': form, 'title': 'Create Funding Round'})

@login_required
def funding_round_edit(request, round_id):
    funding_round = get_object_or_404(FundingRound, id=round_id)
    if request.user.role != 'founder' or funding_round.startup.founder != request.user:
        raise PermissionDenied
        
    old_status = funding_round.status
    if request.method == 'POST':
        form = FundingRoundForm(request.POST, instance=funding_round)
        if form.is_valid():
            rnd = form.save()
            if old_status != rnd.status:
                if rnd.status == 'open':
                    Activity.objects.create(startup=rnd.startup, user=request.user, activity_type='funding_round_opened', description=f"Funding round {rnd.round_name} opened.")
                elif rnd.status == 'closed':
                    Activity.objects.create(startup=rnd.startup, user=request.user, activity_type='funding_round_closed', description=f"Funding round {rnd.round_name} closed.")
            messages.success(request, 'Funding round updated.')
            return redirect('incubator:funding_round_detail', round_id=rnd.id)
    else:
        form = FundingRoundForm(instance=funding_round)
    return render(request, 'incubator/funding_round_form.html', {'form': form, 'title': 'Edit Funding Round'})

# ----------------- FUNDING APPLICATIONS -----------------

@login_required
def funding_application_create(request, round_id):
    if request.user.role != 'investor':
        raise PermissionDenied
        
    funding_round = get_object_or_404(FundingRound, id=round_id)
    if funding_round.status != 'open':
        messages.error(request, "This funding round is not open for applications.")
        return redirect('incubator:funding_round_detail', round_id=funding_round.id)
        
    if FundingApplication.objects.filter(funding_round=funding_round, investor=request.user).exists():
        messages.warning(request, "You have already applied to this round.")
        return redirect('incubator:funding_round_detail', round_id=funding_round.id)

    if request.method == 'POST':
        form = FundingApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.funding_round = funding_round
            app.investor = request.user
            app.save()
            
            Activity.objects.create(startup=funding_round.startup, user=request.user, activity_type='funding_application_submitted', description=f"Funding application submitted by {request.user.username}.")
            Notification.objects.create(
                recipient=funding_round.startup.founder,
                actor=request.user,
                startup=funding_round.startup,
                title="New Funding Application",
                message=f"{request.user.username} submitted a funding application for {funding_round.round_name}.",
                notification_type='funding_application_received',
                link_url=reverse('incubator:funding_application_detail', args=[app.id])
            )
            messages.success(request, 'Application submitted successfully.')
            return redirect('incubator:funding_round_detail', round_id=funding_round.id)
    else:
        form = FundingApplicationForm()
    return render(request, 'incubator/funding_application_form.html', {'form': form, 'round': funding_round})


@login_required
def funding_application_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        applications = FundingApplication.objects.filter(funding_round__startup=startup).order_by('-created_at')
    elif request.user.role == 'investor':
        applications = FundingApplication.objects.filter(investor=request.user).order_by('-created_at')
    else:
        raise PermissionDenied
        
    return render(request, 'incubator/funding_application_list.html', {'applications': applications})

@login_required
def funding_application_detail(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    is_owner = (request.user.role == 'founder' and app.funding_round.startup.founder == request.user)
    is_investor = (request.user == app.investor)
    
    if not (is_owner or is_investor or request.user.role == 'admin'):
        raise PermissionDenied
        
    meetings = app.meetings.all().order_by('-scheduled_at')
    
    if request.method == 'POST' and is_owner:
        new_status = request.POST.get('status')
        if new_status in dict(FundingApplication.STATUS_CHOICES).keys():
            app.status = new_status
            app.responded_at = timezone.now()
            app.save()
            
            # Record activity and notify
            Activity.objects.create(startup=app.funding_round.startup, user=request.user, activity_type='funding_application_status_changed', description=f"Application status changed to {new_status}.")
            
            notif_type_map = {
                'reviewing': 'funding_application_reviewing',
                'accepted': 'funding_application_accepted',
                'rejected': 'funding_application_rejected',
            }
            Notification.objects.create(
                recipient=app.investor,
                actor=request.user,
                startup=app.funding_round.startup,
                title=f"Funding Application {new_status.title()}",
                message=f"Your application for {app.funding_round.round_name} is now {new_status}.",
                notification_type=notif_type_map.get(new_status, 'funding_application_received'),
                link_url=reverse('incubator:funding_application_detail', args=[app.id])
            )
            messages.success(request, f"Status updated to {new_status}.")
            return redirect('incubator:funding_application_detail', app_id=app.id)
            
    return render(request, 'incubator/funding_application_detail.html', {'app': app, 'meetings': meetings, 'is_owner': is_owner, 'is_investor': is_investor})

@login_required
def funding_application_withdraw(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    if request.user != app.investor:
        raise PermissionDenied
    if request.method == 'POST':
        app.status = 'withdrawn'
        app.save()
        messages.success(request, "Application withdrawn.")
    return redirect('incubator:funding_application_detail', app_id=app.id)


# ----------------- INVESTOR MEETINGS -----------------

@login_required
def investor_meeting_create(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    if request.user.role != 'founder' or app.funding_round.startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = InvestorMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.funding_application = app
            meeting.organizer = request.user
            meeting.save()
            
            Activity.objects.create(startup=app.funding_round.startup, user=request.user, activity_type='investor_meeting_scheduled', description=f"Meeting scheduled with {app.investor.username}.")
            Notification.objects.create(
                recipient=app.investor,
                actor=request.user,
                startup=app.funding_round.startup,
                title="Funding Meeting Scheduled",
                message=f"A meeting has been scheduled regarding your application for {app.funding_round.startup.name}.",
                notification_type='funding_meeting_scheduled',
                link_url=reverse('incubator:investor_meeting_detail', args=[meeting.id])
            )
            messages.success(request, 'Meeting scheduled successfully.')
            return redirect('incubator:funding_application_detail', app_id=app.id)
    else:
        form = InvestorMeetingForm()
    return render(request, 'incubator/investor_meeting_form.html', {'form': form, 'app': app})

@login_required
def investor_meeting_detail(request, meeting_id):
    meeting = get_object_or_404(InvestorMeeting, id=meeting_id)
    is_owner = (request.user.role == 'founder' and meeting.funding_application.funding_round.startup.founder == request.user)
    is_investor = (request.user == meeting.funding_application.investor)
    
    if not (is_owner or is_investor or request.user.role == 'admin'):
        raise PermissionDenied
        
    if request.method == 'POST' and is_owner:
        action = request.POST.get('action')
        if action in ['completed', 'cancelled']:
            meeting.status = action
            meeting.save()
            if action == 'cancelled':
                Notification.objects.create(
                    recipient=meeting.funding_application.investor,
                    actor=request.user,
                    startup=meeting.funding_application.funding_round.startup,
                    title="Meeting Cancelled",
                    message=f"Your meeting for {meeting.funding_application.funding_round.startup.name} was cancelled.",
                    notification_type='funding_meeting_cancelled',
                    link_url=reverse('incubator:investor_meeting_detail', args=[meeting.id])
                )
            messages.success(request, f"Meeting marked as {action}.")
        return redirect('incubator:investor_meeting_detail', meeting_id=meeting.id)

    return render(request, 'incubator/investor_meeting_detail.html', {'meeting': meeting, 'is_owner': is_owner, 'is_investor': is_investor})


# ----------------- HIRING & JOB POSTINGS -----------------

@login_required
def job_posting_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        jobs = JobPosting.objects.filter(startup=startup).order_by('-created_at')
        is_founder = True
    else:
        # Public directory
        return redirect('incubator:job_directory')
        
    return render(request, 'incubator/job_posting_list.html', {'jobs': jobs, 'is_founder': is_founder})

@login_required
def job_directory(request):
    query = request.GET.get('q', '')
    emp_type = request.GET.get('employment_type', '')
    exp_level = request.GET.get('experience_level', '')
    
    jobs = JobPosting.objects.filter(status='published').order_by('-created_at')
    
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(startup__name__icontains=query))
    if emp_type:
        jobs = jobs.filter(employment_type=emp_type)
    if exp_level:
        jobs = jobs.filter(experience_level=exp_level)
        
    return render(request, 'incubator/job_directory.html', {'jobs': jobs, 'query': query, 'emp_type': emp_type, 'exp_level': exp_level})

@login_required
def job_posting_detail(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    startup = job.startup
    
    is_owner = (request.user.role == 'founder' and startup.founder == request.user)
    has_access = is_owner or request.user.role in ['admin', 'applicant']
    
    if request.user.role == 'mentor':
        has_access = startup in request.user.mentored_startups.all()
    if request.user.role == 'team_member':
        has_access = startup == get_active_startup(request.user)
    if request.user.role == 'investor' and job.status == 'published':
        has_access = True
        
    if not has_access and job.status != 'published':
        raise PermissionDenied
        
    applications = []
    my_application = None
    if is_owner or request.user.role == 'admin':
        applications = job.applications.all().order_by('-applied_at')
    elif request.user.role == 'applicant':
        my_application = job.applications.filter(applicant=request.user).first()
        
    return render(request, 'incubator/job_posting_detail.html', {
        'job': job, 'applications': applications, 'is_owner': is_owner, 'my_application': my_application
    })

@login_required
def job_posting_create(request):
    if request.user.role != 'founder':
        raise PermissionDenied
    startup = get_active_startup(request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.startup = startup
            job.created_by = request.user
            job.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='job_posting_created', description=f"Job posting {job.title} created.")
            messages.success(request, 'Job posting created.')
            return redirect('incubator:job_posting_list')
    else:
        form = JobPostingForm()
    return render(request, 'incubator/job_posting_form.html', {'form': form, 'title': 'Create Job Posting'})

@login_required
def job_posting_edit(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.user.role != 'founder' or job.startup.founder != request.user:
        raise PermissionDenied
        
    old_status = job.status
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            j = form.save()
            if old_status != j.status:
                if j.status == 'published':
                    Activity.objects.create(startup=j.startup, user=request.user, activity_type='job_published', description=f"Job {j.title} published.")
                elif j.status == 'closed':
                    Activity.objects.create(startup=j.startup, user=request.user, activity_type='job_closed', description=f"Job {j.title} closed.")
            messages.success(request, 'Job posting updated.')
            return redirect('incubator:job_posting_detail', job_id=j.id)
    else:
        form = JobPostingForm(instance=job)
    return render(request, 'incubator/job_posting_form.html', {'form': form, 'title': 'Edit Job Posting'})


# ----------------- JOB APPLICATIONS -----------------

@login_required
def job_application_create(request, job_id):
    if request.user.role != 'applicant':
        messages.error(request, "Only applicants can apply for jobs.")
        return redirect('incubator:job_posting_detail', job_id=job_id)
        
    job = get_object_or_404(JobPosting, id=job_id)
    if job.status != 'published':
        messages.error(request, "This job is not accepting applications.")
        return redirect('incubator:job_posting_detail', job_id=job.id)
        
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('incubator:job_posting_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            app.save()
            
            Activity.objects.create(startup=job.startup, user=request.user, activity_type='job_application_submitted', description=f"Job application submitted by {request.user.username}.")
            Notification.objects.create(
                recipient=job.startup.founder,
                actor=request.user,
                startup=job.startup,
                title="New Job Application",
                message=f"{request.user.username} applied for {job.title}.",
                notification_type='job_application_received',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, 'Application submitted successfully.')
            return redirect('incubator:job_application_list')
    else:
        form = JobApplicationForm()
    return render(request, 'incubator/job_application_form.html', {'form': form, 'job': job})


@login_required
def job_application_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        applications = JobApplication.objects.filter(job__startup=startup).order_by('-applied_at')
    elif request.user.role == 'applicant':
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    else:
        raise PermissionDenied
        
    return render(request, 'incubator/job_application_list.html', {'applications': applications})

@login_required
def job_application_detail(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    is_owner = (request.user.role == 'founder' and app.job.startup.founder == request.user)
    is_applicant = (request.user == app.applicant)
    
    if not (is_owner or is_applicant or request.user.role == 'admin'):
        raise PermissionDenied
        
    interviews = app.interviews.all().order_by('-scheduled_at')
    
    if request.method == 'POST' and is_owner:
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES).keys():
            app.status = new_status
            app.save()
            
            if new_status == 'shortlisted':
                Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='job_application_shortlisted', description=f"Application shortlisted.")
            elif new_status == 'rejected':
                Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='job_application_rejected', description=f"Application rejected.")

            Notification.objects.create(
                recipient=app.applicant,
                actor=request.user,
                startup=app.job.startup,
                title="Application Status Updated",
                message=f"Your application for {app.job.title} is now {new_status}.",
                notification_type='job_application_status_changed',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, f"Status updated to {new_status}.")
            return redirect('incubator:job_application_detail', app_id=app.id)
            
    return render(request, 'incubator/job_application_detail.html', {'app': app, 'interviews': interviews, 'is_owner': is_owner, 'is_applicant': is_applicant})


# ----------------- INTERVIEWS -----------------

@login_required
def interview_create(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    if request.user.role != 'founder' or app.job.startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = app
            interview.interviewer = request.user
            interview.save()
            
            Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='interview_scheduled', description=f"Interview scheduled with {app.applicant.username}.")
            Notification.objects.create(
                recipient=app.applicant,
                actor=request.user,
                startup=app.job.startup,
                title="Interview Scheduled",
                message=f"An interview has been scheduled for your application to {app.job.title}.",
                notification_type='interview_scheduled',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('incubator:job_application_detail', app_id=app.id)
    else:
        form = InterviewForm()
    return render(request, 'incubator/interview_form.html', {'form': form, 'app': app})
