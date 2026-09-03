import os

file_path = 'incubator/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_views = """
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
"""

if 'def team_member_edit' not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(missing_views)
