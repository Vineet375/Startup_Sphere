from django import forms
from .models import Startup

class StartupRegistrationForm(forms.ModelForm):
    class Meta:
        model = Startup
        fields = ['name', 'tagline', 'problem_statement', 'proposed_solution', 'stage', 'category', 'logo']
        widgets = {
            'problem_statement': forms.Textarea(attrs={'rows': 3}),
            'proposed_solution': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['stage'].widget.attrs.update({'class': 'form-select'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
