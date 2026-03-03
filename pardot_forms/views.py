from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from .forms import PardotOptInEmailForm, PardotOptInFullForm, PardotContactForm
from .models import ContactSubmission
import requests
import logging

logger = logging.getLogger(__name__)


def get_pardot_settings(request):
    """
    Get Pardot form settings from Wagtail settings if available, 
    otherwise fall back to Django settings.
    
    Returns a dictionary with:
    - opt_in_form_url: URL for subscription form
    - contact_form_url: URL for contact form
    - email_recipients: List of email addresses for notifications
    - from_email: Email address to use as sender
    """
    # Try to load Wagtail settings first
    try:
        from .wagtail_hooks import PardotFormsSettings
        wagtail_settings = PardotFormsSettings.for_request(request)
        
        return {
            'opt_in_form_url': wagtail_settings.pardot_opt_in_form_url or getattr(settings, 'PARDOT_OPT_IN_FORM_URL', ''),
            'contact_form_url': wagtail_settings.pardot_contact_form_url or getattr(settings, 'PARDOT_CONTACT_FORM_URL', ''),
            'email_recipients': wagtail_settings.get_email_recipients_list() or getattr(settings, 'PARDOT_CONTACT_EMAIL_RECIPIENTS', []),
            'from_email': wagtail_settings.notification_from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
        }
    except (ImportError, AttributeError):
        # Wagtail not installed or settings not configured, use Django settings
        return {
            'opt_in_form_url': getattr(settings, 'PARDOT_OPT_IN_FORM_URL', ''),
            'contact_form_url': getattr(settings, 'PARDOT_CONTACT_FORM_URL', ''),
            'email_recipients': getattr(settings, 'PARDOT_CONTACT_EMAIL_RECIPIENTS', []),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
        }

def email_form_view(request):
    """
    Renders short subscription form.
    """
    if request.method == "POST":
        email_form = PardotOptInEmailForm(request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data["email"]
            request.session["email"] = email
            return redirect("pardot_forms:full_form")
    else:
        email_form = PardotOptInEmailForm()
    return render(request, "pardot_forms/email_form.html", {"email_form": email_form})


def full_form_view(request):
    """
    Renders full subscription form.
    """
    email = request.session.get("email")

    if request.method == "POST":
        full_form = PardotOptInFullForm(request.POST)
        if full_form.is_valid():
            pardot_settings = get_pardot_settings(request)
            pardot_url = pardot_settings['opt_in_form_url']
            data = full_form.cleaned_data
            try:
                response = requests.post(pardot_url, data=data)
                response.raise_for_status()
                return redirect('pardot_forms:subscribe_thank_you')
            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending to Pardot: {e}")
                messages.error(request, "There was an error submitting your form. Please try again.")
    else:
        full_form = PardotOptInFullForm(initial={"email": email})

    return render(request, "pardot_forms/full_form.html", {"full_form": full_form})


def contact_form_view(request):
    """
    Renders contact form.
    """
    if request.method == "POST":
        contact_form = PardotContactForm(request.POST)
        if contact_form.is_valid():
            pardot_settings = get_pardot_settings(request)
            pardot_url = pardot_settings['contact_form_url']
            cleaned_data = contact_form.cleaned_data

            # Save submission to database (will be auto-deleted after 30 days)
            submission = ContactSubmission.objects.create(
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email'],
                phone=cleaned_data.get('phone', ''),
                company=cleaned_data.get('company', ''),
                comments=cleaned_data['comments'],
                opt_in=cleaned_data.get('opt_in', False)
            )

            # Send to Pardot
            try:
                response = requests.post(pardot_url, data=cleaned_data)
                response.raise_for_status()
                submission.sent_to_pardot = True
                submission.save(update_fields=['sent_to_pardot'])
            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending to Pardot: {e}")
                messages.error(request, "There was an error submitting your form. Please try again.")
                return render(request, "pardot_forms/contact_form.html", {"contact_form": contact_form})

            # Send email notification
            email_recipients = pardot_settings['email_recipients']
            if email_recipients:
                subject = f"New contact form submission from {cleaned_data['first_name']} {cleaned_data['last_name']}"
                message = f"Name: {cleaned_data['first_name']} {cleaned_data['last_name']}\nEmail: {cleaned_data['email']}\nCompany: {cleaned_data['company']}\nComments: {cleaned_data['comments']}"
                from_email = pardot_settings['from_email']
                try:
                    send_mail(subject, message, from_email, email_recipients, fail_silently=False)
                    submission.email_sent = True
                    submission.save(update_fields=['email_sent'])
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    messages.warning(request, "Your message was received, but we could not send a notification email.")

            return redirect('pardot_forms:contact_thank_you')
    else:
        contact_form = PardotContactForm()

    return render(request, "pardot_forms/contact_form.html", {"contact_form": contact_form})


def contact_thank_you(request):
    """
    Renders landing page after contact form submission.
    """
    return render(request, "pardot_forms/contact_thank_you.html")


def subscribe_thank_you(request):
    """
    Renders landing page after subscription form submission.
    """
    return render(request, "pardot_forms/subscribe_thank_you.html")
