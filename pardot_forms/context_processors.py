from .forms import PardotOptInEmailForm

def footer_email_form(request):
    return {'display_email_form': PardotOptInEmailForm()}
