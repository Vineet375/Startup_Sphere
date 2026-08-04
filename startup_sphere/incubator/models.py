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
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=250)
    problem_statement = models.TextField()
    proposed_solution = models.TextField()
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='idea')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    logo = models.ImageField(upload_to='startup_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
