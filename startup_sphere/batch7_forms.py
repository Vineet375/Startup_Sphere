
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
