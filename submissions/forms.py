from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    code = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'class': 'code-box'}))

    class Meta:
        model = Submission
        fields = ['code']

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.strip():
            raise forms.ValidationError('Submission cannot be empty.')
        if len(code) > 50_000:
            raise forms.ValidationError('Submission is too large (max 50,000 characters).')
        return code
