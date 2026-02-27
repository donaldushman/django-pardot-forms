from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from .forms import PardotOptInEmailForm, PardotOptInFullForm, PardotContactForm
from .models import ContactSubmission
import requests
import logging

logger = logging.getLogger(__name__)

def email_form_view(request):
    """
    Renders short subscription form. Supports both regular and AJAX requests.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == "POST":
        email_form = PardotOptInEmailForm(request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data["email"]
            request.session["email"] = email
            
            if is_ajax:
                return JsonResponse({'success': True})
            return redirect("full_form")
    else:
        email_form = PardotOptInEmailForm()
    return render(request, "pardot_forms/email_form.html", {"email_form": email_form})


def full_form_view(request):
    """
    Renders full subscription form. Supports both regular and AJAX requests.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    email = request.session.get("email")
    
    if request.method == "POST":
        full_form = PardotOptInFullForm(request.POST)
        if full_form.is_valid():
            pardot_url = settings.PARDOT_OPT_IN_FORM_URL
            data = full_form.cleaned_data
            try:
                response = requests.post(pardot_url, data=data)
                response.raise_for_status()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you for subscribing! We will keep you updated on training and resources.'
                    })
                return redirect('subscribe_thank_you')
            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending to Pardot: {e}")
                if is_ajax:
                    template = "pardot_forms/full_form_modal.html"
                    return JsonResponse({
                        'success': False,
                        'html': render(request, template, 
                                     {"full_form": full_form}).content.decode('utf-8')
                    })
                return redirect('contact_form')
        else:
            # Form has errors
            if is_ajax:
                template = "pardot_forms/full_form_modal.html"
                return JsonResponse({
                    'success': False,
                    'html': render(request, template, 
                                 {"full_form": full_form}).content.decode('utf-8')
                })
    else:
        full_form = PardotOptInFullForm(initial={"email": email})
    
    # Use modal template for AJAX requests, full page template for regular requests
    template = "pardot_forms/full_form_modal.html" if is_ajax else "pardot_forms/full_form.html"
    return render(request, template, {"full_form": full_form})


def contact_form_view(request):
    """
    Renders contact form. Supports both regular and AJAX requests.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == "POST":
        contact_form = PardotContactForm(request.POST)
        if contact_form.is_valid():
            pardot_url = settings.PARDOT_CONTACT_FORM_URL
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
            pardot_success = False
            try:
                response = requests.post(pardot_url, data=cleaned_data)
                response.raise_for_status()
                pardot_success = True
                submission.sent_to_pardot = True
                submission.save(update_fields=['sent_to_pardot'])

            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending to Pardot: {e}")
                if is_ajax:
                    template = "pardot_forms/contact_form_modal.html"
                    return JsonResponse({
                        'success': False,
                        'html': render(request, template, 
                                     {"contact_form": contact_form}).content.decode('utf-8')
                    })
                messages.error(request, "There was an error submitting your form. Please try again.")
                return render(request, "pardot_forms/contact_form.html", {"contact_form": contact_form})
            
            # Send email notification
            email_recipients = getattr(settings, 'PARDOT_CONTACT_EMAIL_RECIPIENTS', [])
            if email_recipients:
                subject = f"New contact form submission from {cleaned_data['first_name']} {cleaned_data['last_name']}"
                message = f"Name: {cleaned_data['first_name']} {cleaned_data['last_name']}\nEmail: {cleaned_data['email']}\nCompany: {cleaned_data['company']}\nComments: {cleaned_data['comments']}"
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
                
                # Attempt to send email
                email_success = False
                try:
                    send_mail(subject, message, from_email, email_recipients, fail_silently=False)
                    email_success = True
                    submission.email_sent = True
                    submission.save(update_fields=['email_sent'])
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    if not is_ajax:
                        messages.warning(request, "Your message was received, but we could not send a notification email.")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for contacting us! We will get back to you soon.'
                })
            return redirect('contact_thank_you')
        else:
            # Form has errors
            if is_ajax:
                template = "pardot_forms/contact_form_modal.html"
                return JsonResponse({
                    'success': False,
                    'html': render(request, template, 
                                 {"contact_form": contact_form}).content.decode('utf-8')
                })
    else:
        contact_form = PardotContactForm()
    
    # Use modal template for AJAX requests, full page template for regular requests
    template = "pardot_forms/contact_form_modal.html" if is_ajax else "pardot_forms/contact_form.html"
    return render(request, template, {"contact_form": contact_form})


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
