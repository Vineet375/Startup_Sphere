import os

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_idea_list = """def idea_list(request):
    startup = get_active_startup(request.user)
    if not startup:
        messages.info(request, "You must register a startup before managing ideas.")
        return redirect('incubator:register_startup')
    ideas = startup.ideas.all().order_by('-updated_at')"""

new_idea_list = """def idea_list(request):
    startup = get_active_startup(request.user)
    if not startup:
        if request.user.role == 'founder':
            messages.info(request, "You must register a startup before managing ideas.")
            return redirect('incubator:register_startup')
        else:
            messages.error(request, "You are not associated with any startup.")
            return redirect('dashboard:home')
            
    ideas = startup.ideas.all().order_by('-updated_at')"""

if old_idea_list in content:
    content = content.replace(old_idea_list, new_idea_list)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
