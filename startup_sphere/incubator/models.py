from django.db import models
from django.conf import settings

class Startup(models.Model):
    STAGE_CHOICES = (
        ('idea', 'Idea Stage'),
        ('prototype', 'Prototype / MVP'),
        ('seed', 'Pre-Seed / Seed'),
        ('growth', 'Early Growth'),
        ('expansion', 'Expansion / Scaling'),
    )

    CATEGORY_CHOICES = (
        ('tech', 'Technology & Software'),
        ('health', 'Healthcare & MedTech'),
        ('finance', 'FinTech'),
        ('edu', 'EdTech'),
        ('ecommerce', 'E-Commerce & Retail'),
        ('other', 'Other'),
    )
    
    INCUBATION_CHOICES = (
        ('idea_stage', 'Idea Stage'),
        ('under_review', 'Under Review'),
        ('incubating', 'Incubating'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    founder = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='startup')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_startups', limit_choices_to={'role': 'mentor'})
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=250)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='idea')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    incubation_status = models.CharField(max_length=20, choices=INCUBATION_CHOICES, default='idea_stage')
    logo = models.ImageField(upload_to='startup_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Idea(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='ideas')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ideas')
    title = models.CharField(max_length=200)
    description = models.TextField()
    problem_statement = models.TextField(default='')
    proposed_solution = models.TextField(default='')
    industry = models.CharField(max_length=50, blank=True, null=True)
    target_audience = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    under_review_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='feedbacks')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.mentor.username} on {self.idea.title}"

class Milestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.startup.name}"

class Activity(models.Model):
    ACTIVITY_TYPES = (
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
    )
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_activity_type_display()}] {self.startup.name} - {self.created_at.date()}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
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
    )
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='actor_notifications')
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    link_url = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

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
