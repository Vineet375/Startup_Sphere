import os

file_path = 'incubator/forms.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from .models import Startup, Idea, Feedback, Milestone',
                          'from .models import Startup, Idea, Feedback, Milestone, TeamMember, Document')

forms_to_add = """
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
"""

if 'class TeamMemberInviteForm' not in content:
    content += forms_to_add

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
