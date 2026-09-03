import re

with open('incubator/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix ACTIVITY_TYPES
pattern = re.compile(r'    ACTIVITY_TYPES = \(\n.*?\n    \)(?:.*?)\)\n', re.DOTALL)
match = pattern.search(content)

fixed_activity_types = """    ACTIVITY_TYPES = (
        ('startup_registered', 'Startup Registered'),
        ('mentor_assigned', 'Mentor Assigned'),
        ('mentor_changed', 'Mentor Changed'),
        ('mentor_removed', 'Mentor Removed'),
        ('status_changed', 'Status Changed'),
        ('idea_submitted', 'Idea Submitted'),
        ('idea_under_review', 'Idea Under Review'),
        ('feedback_added', 'Feedback Added'),
        ('milestone_created', 'Milestone Created'),
        ('milestone_updated', 'Milestone Updated'),
        ('milestone_completed', 'Milestone Completed'),
        ('team_member_added', 'Team Member Added'),
        ('pending_invitation_created', 'Pending Invitation Created'),
        ('team_member_removed', 'Team Member Removed'),
        ('team_member_updated', 'Team Member Updated'),
        ('document_uploaded', 'Document Uploaded'),
        ('document_deleted', 'Document Deleted'),
        ('document_updated', 'Document Updated'),
    )\n"""

if match:
    pass # we could replace, but wait, it might be simpler to just find the `class Activity` block and replace up to `startup = `
    
content = re.sub(r'    ACTIVITY_TYPES = \(.*?\)\n.*?\)  # if it matched extra?', '', content, flags=re.DOTALL) # wait, regex is tricky

# Safer way
lines = content.split('\n')
out_lines = []
skip = False
in_activity = False
in_notification = False

for line in lines:
    if line.startswith('    ACTIVITY_TYPES = ('):
        skip = True
        in_activity = True
        out_lines.append(fixed_activity_types.strip('\n'))
        continue
    
    if line.startswith('    NOTIFICATION_TYPES = ('):
        skip = True
        in_notification = True
        out_lines.append("""    NOTIFICATION_TYPES = (
        ('mentor_assigned', 'Mentor Assigned'),
        ('mentor_changed', 'Mentor Changed'),
        ('startup_status_changed', 'Startup Status Changed'),
        ('idea_submitted', 'Idea Submitted'),
        ('idea_under_review', 'Idea Under Review'),
        ('feedback_received', 'Feedback Received'),
        ('milestone_created', 'Milestone Created'),
        ('milestone_completed', 'Milestone Completed'),
        ('team_member_added', 'Team Member Added'),
        ('document_uploaded', 'Document Uploaded'),
    )""")
        continue
        
    if skip and in_activity:
        if line.strip() == "startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='activities')":
            skip = False
            in_activity = False
            out_lines.append(line)
        continue
            
    if skip and in_notification:
        if line.strip() == "recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')":
            skip = False
            in_notification = False
            out_lines.append(line)
        continue
        
    if not skip:
        out_lines.append(line)
        
with open('incubator/models.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
