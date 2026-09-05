import os

file_path = 'incubator/forms.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_form = """
from .models import Evaluation

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'innovation_score', 
            'market_potential_score', 
            'business_model_score', 
            'team_score', 
            'execution_score', 
            'comments'
        ]
        widgets = {
            'innovation_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'market_potential_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'business_model_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'team_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'execution_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
"""

if "class EvaluationForm" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(new_form)
