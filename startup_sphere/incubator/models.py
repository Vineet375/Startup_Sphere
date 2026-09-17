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
        ('evaluation_received', 'Evaluation Received'),
        ('document_deleted', 'Document Deleted'),
        ('document_updated', 'Document Updated'),
        ('evaluation_created', 'Evaluation Created'),
        ('evaluation_updated', 'Evaluation Updated'),
        ('event_created', 'Event Created'),
        ('event_updated', 'Event Updated'),
        ('event_cancelled', 'Event Cancelled'),
        ('event_registered', 'Event Registered'),
        ('event_unregistered', 'Event Unregistered'),
        ('attendance_marked', 'Attendance Marked'),
        ('collaboration_request_sent', 'Collaboration Request Sent'),
        ('collaboration_request_accepted', 'Collaboration Request Accepted'),
        ('collaboration_request_rejected', 'Collaboration Request Rejected'),
        ('collaboration_request_cancelled', 'Collaboration Request Cancelled'),
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
        ('evaluation_received', 'Evaluation Received'),
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

from django.core.validators import MinValueValidator, MaxValueValidator

class Evaluation(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations_given')
    
    innovation_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    market_potential_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    business_model_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    team_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    execution_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    overall_score = models.FloatField(blank=True, null=True)
    
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['startup', 'evaluator'], name='unique_evaluation')
        ]

    def save(self, *args, **kwargs):
        self.overall_score = sum([
            self.innovation_score, 
            self.market_potential_score, 
            self.business_model_score, 
            self.team_score, 
            self.execution_score
        ]) / 5.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation for {self.startup.name} by {self.evaluator.username}"


class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('workshop', 'Workshop'),
        ('mentoring', 'Mentoring Session'),
        ('pitch', 'Pitch Event'),
        ('investor_meet', 'Investor Meet'),
        ('networking', 'Networking Event'),
        ('incubation', 'Incubation Session'),
        ('seminar', 'Entrepreneurship Seminar'),
        ('demo_day', 'Demo Day'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='workshop')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    venue = models.CharField(max_length=255, blank=True, null=True)
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class EventParticipation(models.Model):
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participations')
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'participant'], name='unique_event_participation')
        ]

    def __str__(self):
        return f"{self.participant.username} - {self.event.title}"


class CollaborationRequest(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('startup_collaboration', 'Startup Collaboration'),
        ('mentorship', 'Mentorship'),
        ('networking', 'Networking'),
        ('partnership', 'Partnership'),
        ('project', 'Project'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_collaboration_requests')
    requester_startup = models.ForeignKey(Startup, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_collaboration_requests')
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_collaboration_requests')
    recipient_startup = models.ForeignKey(Startup, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_collaboration_requests')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, default='networking')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.requester.username} to {self.recipient.username} - {self.get_status_display()}"

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
