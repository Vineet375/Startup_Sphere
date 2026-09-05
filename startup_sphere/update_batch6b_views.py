import os
import re

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_views = """
from django.db.models import Q
from .models import Evaluation
from .forms import EvaluationForm

@login_required
def startup_directory(request):
    startups = Startup.objects.all().order_by('-created_at')
    
    q = request.GET.get('q')
    industry = request.GET.get('industry')
    status = request.GET.get('status')
    
    if q:
        startups = startups.filter(
            Q(name__icontains=q) | 
            Q(tagline__icontains=q) | 
            Q(industry__icontains=q)
        )
    if industry:
        startups = startups.filter(industry__icontains=industry)
    if status:
        startups = startups.filter(status=status)
        
    return render(request, 'incubator/startup_directory.html', {
        'startups': startups,
        'q': q,
        'industry': industry,
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
    
    if not (is_founder or is_assigned_mentor or is_admin):
        raise PermissionDenied("You do not have permission to view this startup's evaluations.")
        
    evaluations = startup.evaluations.all().order_by('-updated_at')
    
    user_evaluation = None
    if is_assigned_mentor:
        user_evaluation = evaluations.filter(evaluator=request.user).first()
        
    avg_overall = evaluations.aggregate(models.Avg('overall_score'))['overall_score__avg']
    
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
                link_url=f'/startups/{startup.id}/evaluations/'
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
"""

if "def startup_directory" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(new_views)
