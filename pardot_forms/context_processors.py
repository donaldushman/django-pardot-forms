from .forms import PardotOptInEmailForm, PardotContactForm, PardotOptInFullForm

def pardot_forms(request):
    return {
        'display_email_form': PardotOptInEmailForm(),
        'contact_form': PardotContactForm(),
        'full_form': PardotOptInFullForm(),
    }
