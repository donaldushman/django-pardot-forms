from django import forms
from turnstile.fields import TurnstileField

class PardotOptInEmailForm(forms.Form):
    """
    Short subscription form. Gets the visitor's email address and passes it to the full form.
    """
    email = forms.EmailField(required=True, label="Your email address", max_length=200, widget=forms.EmailInput(
           attrs={'placeholder': 'Your email address'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = "" # Remove colon
    
class PardotOptInFullForm(forms.Form):
    """
    Full subscription form. Connects to Pardot opt-in form handler.
    """
    first_name = forms.CharField(required=False, max_length=100)
    last_name = forms.CharField(required=False, max_length=100)
    company = forms.CharField(required=False, max_length=100)
    email = forms.EmailField(required=True, max_length=200, label='Email*')
    pardot_extra_field = forms.CharField(required=False, label="Additional comments")
    turnstile = TurnstileField(label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = "" # Remove colon


class PardotContactForm(forms.Form):
    """
    Contact form. Connects to Pardot contact form handler.
    """
    first_name = forms.CharField(required=False, max_length=100)
    last_name = forms.CharField(required=False, max_length=100)
    company = forms.CharField(required=False, max_length=100)
    email = forms.EmailField(required=True, max_length=200, label='Email*')
    phone = forms.CharField(required=False, max_length=11, label="Phone Number")
    comments = forms.CharField(required=False, max_length=255, label="How can we help?", widget=forms.Textarea(attrs={'rows': 5, 'style': 'width: 100%;'}))
    opt_in = forms.BooleanField(required=False, label="Subscribe to receive email updates.")
    pardot_extra_field = forms.CharField(required=False, label="Additional comments")
    turnstile = TurnstileField(label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = "" # Remove colon

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('pardot_extra_field')
        if honeypot:
            raise forms.ValidationError("Spam detected.")
        return cleaned_data
