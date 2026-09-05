import os

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_startup_detail = """def startup_detail(request, startup_id=None):
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
            
    milestones = startup.milestones.all().order_by('target_date')
    return render(request, 'incubator/startup_detail.html', {'startup': startup, 'milestones': milestones})"""

new_startup_detail = """def startup_detail(request, startup_id=None):
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
    })"""

if old_startup_detail in content:
    content = content.replace(old_startup_detail, new_startup_detail)
else:
    print("Could not find old_startup_detail")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
