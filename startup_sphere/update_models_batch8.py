import os

file_path = 'incubator/models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update Activity Types
new_activity_choices = """        ('collaboration_request_cancelled', 'Collaboration Request Cancelled'),
        ('funding_round_created', 'Funding Round Created'),
        ('funding_round_opened', 'Funding Round Opened'),
        ('funding_round_closed', 'Funding Round Closed'),
        ('funding_application_submitted', 'Funding Application Submitted'),
        ('funding_application_status_changed', 'Funding Application Status Changed'),
        ('investor_meeting_scheduled', 'Investor Meeting Scheduled'),
        ('job_posting_created', 'Job Posting Created'),
        ('job_published', 'Job Published'),
        ('job_closed', 'Job Closed'),
        ('job_application_submitted', 'Job Application Submitted'),
        ('job_application_shortlisted', 'Job Application Shortlisted'),
        ('job_application_rejected', 'Job Application Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('pitch_deck_uploaded', 'Pitch Deck Uploaded'),
        ('pitch_deck_updated', 'Pitch Deck Updated'),
    )"""

content = content.replace("        ('collaboration_request_cancelled', 'Collaboration Request Cancelled'),\n    )", new_activity_choices)

# Update Notification Types
new_notification_choices = """        ('collaboration_cancelled', 'Collaboration Cancelled'),
        ('funding_application_received', 'Funding Application Received'),
        ('funding_application_reviewing', 'Funding Application Reviewing'),
        ('funding_application_accepted', 'Funding Application Accepted'),
        ('funding_application_rejected', 'Funding Application Rejected'),
        ('funding_meeting_scheduled', 'Funding Meeting Scheduled'),
        ('funding_meeting_cancelled', 'Funding Meeting Cancelled'),
        ('job_application_received', 'Job Application Received'),
        ('job_application_status_changed', 'Job Application Status Changed'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_rescheduled', 'Interview Rescheduled'),
        ('interview_cancelled', 'Interview Cancelled'),
    )"""

content = content.replace("        ('collaboration_cancelled', 'Collaboration Cancelled'),\n    )", new_notification_choices)


new_models = """
from decimal import Decimal

class InvestorProfile(models.Model):
    INVESTOR_TYPE_CHOICES = (
        ('angel', 'Angel Investor'),
        ('vc', 'Venture Capital'),
        ('corporate', 'Corporate Investor'),
        ('seed', 'Seed Fund'),
        ('accelerator', 'Accelerator'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investor_profile')
    investor_type = models.CharField(max_length=50, choices=INVESTOR_TYPE_CHOICES, default='angel')
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    investment_focus = models.CharField(max_length=255, blank=True, null=True)
    preferred_industries = models.CharField(max_length=255, blank=True, null=True)
    preferred_startup_stages = models.CharField(max_length=255, blank=True, null=True)
    min_investment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    max_investment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Investor Profile - {self.user.username}"


class FundingRound(models.Model):
    ROUND_TYPE_CHOICES = (
        ('pre_seed', 'Pre-Seed'),
        ('seed', 'Seed'),
        ('series_a', 'Series A'),
        ('series_b', 'Series B'),
        ('series_c', 'Series C'),
        ('bridge', 'Bridge'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )

    startup = models.ForeignKey('Startup', on_delete=models.CASCADE, related_name='funding_rounds')
    round_name = models.CharField(max_length=200)
    round_type = models.CharField(max_length=50, choices=ROUND_TYPE_CHOICES, default='seed')
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    minimum_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    raised_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    valuation = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    equity_offered = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))])
    opening_date = models.DateField()
    closing_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.round_name} - {self.startup.name}"


class FundingApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )

    funding_round = models.ForeignKey(FundingRound, on_delete=models.CASCADE, related_name='applications')
    investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='funding_applications')
    requested_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['funding_round', 'investor'], name='unique_funding_application')
        ]

    def __str__(self):
        return f"{self.investor.username} -> {self.funding_round.round_name}"


class InvestorMeeting(models.Model):
    MEETING_TYPE_CHOICES = (
        ('online', 'Online'),
        ('in_person', 'In Person'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )

    funding_application = models.ForeignKey(FundingApplication, on_delete=models.CASCADE, related_name='meetings')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_investor_meetings')
    scheduled_at = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=60)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='online')
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Meeting: {self.funding_application.investor.username} - {self.funding_application.funding_round.startup.name}"


class JobPosting(models.Model):
    EMPLOYMENT_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
    )

    EXPERIENCE_CHOICES = (
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead/Manager'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    )

    startup = models.ForeignKey('Startup', on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    location = models.CharField(max_length=255, blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    application_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.startup.name}"


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    )

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])])
    cover_letter = models.TextField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    notes = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'applicant'], name='unique_job_application')
        ]

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


class Interview(models.Model):
    MEETING_TYPE_CHOICES = (
        ('online', 'Online'),
        ('in_person', 'In Person'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conducted_interviews')
    scheduled_at = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=60)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='online')
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interview: {self.application.applicant.username} - {self.application.job.title}"
"""

if "class InvestorProfile" not in content:
    content += new_models
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
