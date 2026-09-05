import os
import re

file_path = 'incubator/models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update ACTIVITY_TYPES
if "'evaluation_created'" not in content:
    content = content.replace(
        "('document_updated', 'Document Updated'),",
        "('document_updated', 'Document Updated'),\n        ('evaluation_created', 'Evaluation Created'),\n        ('evaluation_updated', 'Evaluation Updated'),"
    )

# 2. Update NOTIFICATION_TYPES
if "'evaluation_received'" not in content:
    content = content.replace(
        "('document_uploaded', 'Document Uploaded'),",
        "('document_uploaded', 'Document Uploaded'),\n        ('evaluation_received', 'Evaluation Received'),"
    )

# 3. Add Evaluation model
new_model = """
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
"""

if "class Evaluation" not in content:
    content += new_model

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
