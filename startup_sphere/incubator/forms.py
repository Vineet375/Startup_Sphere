from django import forms
from .models import Startup, Idea, Feedback, Milestone, TeamMember, Document

class StartupForm(forms.ModelForm):
    class Meta:
        model = Startup
        fields = ['name', 'tagline', 'stage', 'category', 'logo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['stage'].widget.attrs.update({'class': 'form-select'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'description', 'problem_statement', 'proposed_solution', 'target_audience', 'industry']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'problem_statement': forms.Textarea(attrs={'rows': 3}),
            'proposed_solution': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your feedback here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'target_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        if 'status' in self.fields:
            self.fields['status'].widget.attrs.update({'class': 'form-select'})

from django.core.exceptions import ValidationError

class TeamMemberInviteForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = TeamMember
        fields = ['position', 'custom_position']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['position'].widget.attrs.update({'class': 'form-select'})
        
class TeamMemberUpdateForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['position', 'custom_position']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['position'].widget.attrs.update({'class': 'form-select'})

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'category', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Document file too large ( > 5MB ).")
            # We also rely on FileExtensionValidator in the model for extension validation.
            
            # Simple content type check
            allowed_content_types = [
                'application/pdf', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            ]
            content_type = getattr(file, 'content_type', '')
            # If content_type is provided and not in allowed list, raise validation error.
            # But sometimes browsers send generic content types, so we can't be too strict.
            # We'll stick to basic checking if it exists.
            if content_type and content_type not in allowed_content_types and 'application/octet-stream' not in content_type:
                # We won't raise error on octet-stream because some OS might just default to it, but we rely on extension.
                pass
                
        return file

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
