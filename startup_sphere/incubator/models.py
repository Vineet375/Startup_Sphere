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

    founder = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='startup')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_startups', limit_choices_to={'role': 'mentor'})
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=250)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='idea')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
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
