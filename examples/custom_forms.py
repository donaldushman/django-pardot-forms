"""
Example: Extending django-pardot-forms with custom fields

This example shows how to extend the PardotContactForm with additional
fields like phone number and company name.
"""

from django import forms
from pardot_forms.forms import PardotContactForm


class CustomContactForm(PardotContactForm):
    """
    Extended contact form with phone and company fields.
    
    This form inherits all the fields from PardotContactForm (name, email, 
    comments, cf_turnstile_response) and adds custom fields.
    """
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)'
        })
    )
    
    company = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name'
        })
    )
    
    # Optional: reorder fields
    field_order = ['name', 'email', 'company', 'phone', 'comments', 'cf_turnstile_response']
    
    def clean_phone(self):
        """Optional: Add custom validation for phone field"""
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Remove common separators
            phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not phone.isdigit():
                raise forms.ValidationError('Please enter a valid phone number')
        return phone


class JobApplicationForm(PardotContactForm):
    """
    Example: Job application form with position and resume fields.
    """
    position = forms.ChoiceField(
        choices=[
            ('', 'Select Position'),
            ('engineer', 'Software Engineer'),
            ('designer', 'UX Designer'),
            ('manager', 'Product Manager'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    resume_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Link to Resume/Portfolio (optional)'
        }),
        help_text='Provide a link to your resume, LinkedIn, or portfolio'
    )
    
    field_order = ['name', 'email', 'position', 'resume_url', 'comments', 'cf_turnstile_response']
