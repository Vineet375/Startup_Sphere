import os
import re

file_path = 'incubator/models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update ACTIVITY_TYPES
if "('collaboration_request_sent', 'Collaboration Request Sent')" not in content:
    activity_replacement = """        ('evaluation_updated', 'Evaluation Updated'),
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
    )"""
    content = content.replace("        ('evaluation_updated', 'Evaluation Updated'),\n    )", activity_replacement)

# Update NOTIFICATION_TYPES
if "('event_registered', 'Event Registered')" not in content:
    notification_replacement = """        ('evaluation_received', 'Evaluation Received'),
        ('event_registered', 'Event Registered'),
        ('event_cancelled_notify', 'Event Cancelled Notify'),
        ('event_reminder', 'Event Reminder'),
        ('collaboration_received', 'Collaboration Received'),
        ('collaboration_accepted', 'Collaboration Accepted'),
        ('collaboration_rejected', 'Collaboration Rejected'),
        ('collaboration_cancelled', 'Collaboration Cancelled'),
    )"""
    content = content.replace("        ('evaluation_received', 'Evaluation Received'),\n    )", notification_replacement)

# Define new models
new_models = """

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
"""

if "class Event(models.Model):" not in content:
    content += new_models

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
