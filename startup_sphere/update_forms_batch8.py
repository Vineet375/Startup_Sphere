import os

file_path = 'incubator/forms.py'
new_forms = """
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
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(new_forms)
