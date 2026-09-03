import os
import re

file_path = 'incubator/models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add TeamMember and Document models
models_to_add = """
from django.core.validators import FileExtensionValidator

class TeamMember(models.Model):
    POSITION_CHOICES = (
        ('founder', 'Founder'),
        ('cofounder', 'Co-Founder'),
        ('cto', 'CTO'),
        ('ceo', 'CEO'),
        ('coo', 'COO'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
    )

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='startup_teams')
    invited_email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='other')
    custom_position = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.startup.name}"
        return f"{self.invited_email} (Pending) - {self.startup.name}"

class Document(models.Model):
    CATEGORY_CHOICES = (
        ('pitch_deck', 'Pitch Deck'),
        ('business_plan', 'Business Plan'),
        ('financial', 'Financial Document'),
        ('product', 'Product Document'),
        ('legal', 'Legal Document'),
        ('market_research', 'Market Research'),
        ('other', 'Other'),
    )

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    file = models.FileField(
        upload_to='startup_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])]
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.startup.name}"
"""

if 'class TeamMember' not in content:
    content += models_to_add

# Update Activity
activity_types_replacement = """    ACTIVITY_TYPES = (
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
    )"""

content = re.sub(r'    ACTIVITY_TYPES = \(.*?\)', activity_types_replacement, content, flags=re.DOTALL)

# Update Notification
notification_types_replacement = """    NOTIFICATION_TYPES = (
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
    )"""

content = re.sub(r'    NOTIFICATION_TYPES = \(.*?\)', notification_types_replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
