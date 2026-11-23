from django import forms
from django.utils import timezone

from .models import Assignment


class AssignmentForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Assignment
        fields = ['title', 'slug', 'description', 'language', 'deadline', 'similarity_threshold']

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError('Deadline must be in the future.')
        return deadline

    def clean_similarity_threshold(self):
        value = self.cleaned_data['similarity_threshold']
        if not (0 < value <= 100):
            raise forms.ValidationError('Threshold must be between 1 and 100.')
        return value
