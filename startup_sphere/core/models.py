from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('founder', 'Founder'),
        ('mentor', 'Mentor'),
        ('investor', 'Investor'),
        ('applicant', 'Applicant'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='founder')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
