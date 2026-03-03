from .forms import PardotOptInEmailForm, PardotContactForm, PardotOptInFullForm

def pardot_forms(request):
    email = request.session.get('email', '')
    return {
        'display_email_form': PardotOptInEmailForm(),
        'contact_form': PardotContactForm(),
        'full_form': PardotOptInFullForm(initial={'email': email}),
    }
