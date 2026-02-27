"""
Example: Custom views for extended forms

These views handle the custom forms and can either:
1. Store extra data in the comments field (simple approach)
2. Store in a custom model (advanced approach - see custom_models.py)
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings

from pardot_forms.models import ContactSubmission
from .custom_forms import CustomContactForm, JobApplicationForm

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def custom_contact_view(request):
    """
    Handle the custom contact form with phone and company fields.
    
    This stores the extra fields in the comments field as JSON,
    keeping existing data separate.
    """
    if request.method == 'POST':
        form = CustomContactForm(request.POST)
        
        if form.is_valid():
            # Extract custom fields
            phone = form.cleaned_data.get('phone', '')
            company = form.cleaned_data.get('company', '')
            original_comments = form.cleaned_data.get('comments', '')
            
            # Format the data for storage
            # Option 1: Store as formatted text
            formatted_comments = f"""Company: {company}
Phone: {phone or 'Not provided'}

Message:
{original_comments}"""
            
            # Option 2: Store as JSON (easier to parse later)
            data = {
                'company': company,
                'phone': phone,
                'message': original_comments
            }
            formatted_comments = json.dumps(data)
            
            # Save to database
            submission = ContactSubmission.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                comments=formatted_comments,
                opt_in=False  # Not a subscription
            )
            
            # Send notification email
            try:
                subject = f'New Custom Contact Form: {company}'
                message = f"""
New contact form submission:

Name: {form.cleaned_data['name']}
Email: {form.cleaned_data['email']}
Company: {company}
Phone: {phone or 'Not provided'}

Message:
{original_comments}
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.PARDOT_FORMS_NOTIFICATION_EMAIL],
                    fail_silently=False,
                )
                submission.email_sent = True
                submission.save()
            except Exception as e:
                logger.error(f'Failed to send notification email: {e}')
            
            # Check if AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! We will be in touch soon.'
                })
            
            return render(request, 'pardot_forms/contact_thank_you.html')
        
        else:
            # Form validation failed
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            
            return render(request, 'your_app/custom_contact_form.html', {
                'form': form
            })
    
    # GET request
    form = CustomContactForm()
    return render(request, 'your_app/custom_contact_form.html', {
        'form': form
    })


@require_http_methods(["GET", "POST"])
def job_application_view(request):
    """
    Handle job application form submissions.
    """
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        
        if form.is_valid():
            # Store application data as JSON
            application_data = {
                'position': form.cleaned_data.get('position'),
                'resume_url': form.cleaned_data.get('resume_url', ''),
                'cover_letter': form.cleaned_data.get('comments', '')
            }
            
            submission = ContactSubmission.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                comments=json.dumps(application_data),
                opt_in=False
            )
            
            # Send notification
            try:
                position_display = dict(form.fields['position'].choices).get(
                    form.cleaned_data['position']
                )
                subject = f'Job Application: {position_display}'
                message = f"""
New job application received:

Name: {form.cleaned_data['name']}
Email: {form.cleaned_data['email']}
Position: {position_display}
Resume: {form.cleaned_data.get('resume_url') or 'Not provided'}

Cover Letter:
{form.cleaned_data.get('comments', '')}
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.PARDOT_FORMS_NOTIFICATION_EMAIL],
                    fail_silently=False,
                )
                submission.email_sent = True
                submission.save()
            except Exception as e:
                logger.error(f'Failed to send application email: {e}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Application submitted successfully!'
                })
            
            return render(request, 'your_app/application_thank_you.html')
        
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            
            return render(request, 'your_app/job_application_form.html', {
                'form': form
            })
    
    form = JobApplicationForm()
    return render(request, 'your_app/job_application_form.html', {
        'form': form
    })
