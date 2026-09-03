import re

with open('incubator/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper logic to check team membership
helper_logic = """
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
"""

# Inject helper logic right after imports
# find first "@login_required" to inject before it
idx = content.find("@login_required")
content = content[:idx] + helper_logic + "\n" + content[idx:]

# Rewrite startup_detail
startup_detail_old = """def startup_detail(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
        if request.user != startup.founder and request.user != startup.mentor and request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to view this startup.")
    else:
        try:
            startup = request.user.startup
        except Startup.DoesNotExist:
            messages.info(request, "You haven't registered a startup yet.")
            return redirect('incubator:register_startup')"""

startup_detail_new = """def startup_detail(request, startup_id=None):
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
            return redirect('incubator:register_startup')"""
content = content.replace(startup_detail_old, startup_detail_new)

# Rewrite idea_list
idea_list_old = """def idea_list(request):
    try:
        startup = request.user.startup
        ideas = startup.ideas.all().order_by('-updated_at')
    except Startup.DoesNotExist:
        messages.info(request, "You must register a startup before managing ideas.")
        return redirect('incubator:register_startup')"""

idea_list_new = """def idea_list(request):
    startup = get_active_startup(request.user)
    if not startup:
        messages.info(request, "You must register a startup before managing ideas.")
        return redirect('incubator:register_startup')
    ideas = startup.ideas.all().order_by('-updated_at')"""
content = content.replace(idea_list_old, idea_list_new)

# Rewrite idea_detail
idea_detail_old = """def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.user != idea.creator and request.user != idea.startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("You do not have permission to view this idea.")"""

idea_detail_new = """def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    startup = idea.startup
    is_founder = request.user == startup.founder
    is_mentor = request.user == startup.mentor
    is_admin = request.user.role == 'admin'
    is_team = is_active_team_member(request.user, startup)
    if not (is_founder or is_mentor or is_admin or is_team):
        raise PermissionDenied("You do not have permission to view this idea.")"""
content = content.replace(idea_detail_old, idea_detail_new)

# Add Team Management & Document Views
new_views = """

@login_required
def team_list(request):
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
"""

content += new_views

with open('incubator/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
