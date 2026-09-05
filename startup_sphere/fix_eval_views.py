import os

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix evaluation_list view to allow team members
old_eval_list_perm = """    is_founder = (request.user == startup.founder)
    is_assigned_mentor = (request.user == startup.mentor)
    is_admin = request.user.role == 'admin'
    
    if not (is_founder or is_assigned_mentor or is_admin):
        raise PermissionDenied("You do not have permission to view this startup's evaluations.")"""

new_eval_list_perm = """    is_founder = (request.user == startup.founder)
    is_assigned_mentor = (request.user == startup.mentor)
    is_admin = request.user.role == 'admin'
    is_active_team_member = startup.team_members.filter(user=request.user, status='active').exists()
    
    if not (is_founder or is_assigned_mentor or is_admin or is_active_team_member):
        raise PermissionDenied("You do not have permission to view this startup's evaluations.")"""

if old_eval_list_perm in content:
    content = content.replace(old_eval_list_perm, new_eval_list_perm)
else:
    print("Could not find old_eval_list_perm in views.py")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
