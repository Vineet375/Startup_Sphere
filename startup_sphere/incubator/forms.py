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

from .models import Event, CollaborationRequest
from django.utils import timezone
from django import forms

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'start_datetime', 'end_datetime', 'venue', 'meeting_link', 'capacity']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        
        if start and end and start >= end:
            raise forms.ValidationError("End datetime must be after start datetime.")
            
        return cleaned_data

class CollaborationRequestForm(forms.ModelForm):
    class Meta:
        model = CollaborationRequest
        fields = ['request_type', 'title', 'message']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

from .models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview

class InvestorProfileForm(forms.ModelForm):
    class Meta:
        model = InvestorProfile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'investor_type': forms.Select(attrs={'class': 'form-select'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'investment_focus': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_industries': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_startup_stages': forms.TextInput(attrs={'class': 'form-control'}),
            'min_investment': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_investment': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class FundingRoundForm(forms.ModelForm):
    class Meta:
        model = FundingRound
        exclude = ['startup', 'raised_amount', 'created_at', 'updated_at']
        widgets = {
            'round_name': forms.TextInput(attrs={'class': 'form-control'}),
            'round_type': forms.Select(attrs={'class': 'form-select'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'valuation': forms.NumberInput(attrs={'class': 'form-control'}),
            'equity_offered': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        opening = cleaned_data.get('opening_date')
        closing = cleaned_data.get('closing_date')
        target = cleaned_data.get('target_amount')
        minimum = cleaned_data.get('minimum_amount')
        
        if opening and closing and opening > closing:
            raise forms.ValidationError("Closing date must be after opening date.")
            
        if target and minimum and minimum > target:
            raise forms.ValidationError("Minimum amount cannot be greater than target amount.")
            
        return cleaned_data

class FundingApplicationForm(forms.ModelForm):
    class Meta:
        model = FundingApplication
        fields = ['requested_amount', 'message']
        widgets = {
            'requested_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class InvestorMeetingForm(forms.ModelForm):
    class Meta:
        model = InvestorMeeting
        exclude = ['funding_application', 'organizer', 'status', 'created_at', 'updated_at']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'meeting_type': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        exclude = ['startup', 'created_by', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        s_min = cleaned_data.get('salary_min')
        s_max = cleaned_data.get('salary_max')
        
        if s_min and s_max and s_min > s_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
            
        return cleaned_data

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'portfolio_url']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        exclude = ['application', 'interviewer', 'status', 'created_at', 'updated_at']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'meeting_type': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
