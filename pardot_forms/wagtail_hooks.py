"""
Wagtail integration for django-pardot-forms.

This module provides a Wagtail settings panel for configuring Pardot form URLs
and email recipients through the Wagtail admin interface.
"""

from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


@register_setting
class PardotFormsSettings(BaseSiteSetting):
    """
    Wagtail site settings for Pardot forms configuration.
    
    These settings can be accessed in views and templates via:
    - Views: PardotFormsSettings.for_request(request) or PardotFormsSettings.for_site(site)
    - Templates: {% load wagtailsettings_tags %} {% get_settings %}
    
    The settings will appear in the Wagtail admin under Settings > Pardot Forms.
    """
    
    # Pardot form URLs
    pardot_opt_in_form_url = models.URLField(
        verbose_name='Subscription Form URL',
        help_text='Pardot URL for the opt-in/subscription form',
        blank=True,
        max_length=500
    )
    
    pardot_contact_form_url = models.URLField(
        verbose_name='Contact Form URL',
        help_text='Pardot URL for the contact form',
        blank=True,
        max_length=500
    )
    
    # Email notification settings
    contact_email_recipients = models.TextField(
        verbose_name='Contact Form Email Recipients',
        help_text='Email addresses to receive contact form notifications (one per line)',
        blank=True
    )
    
    notification_from_email = models.EmailField(
        verbose_name='Notification From Email',
        help_text='Email address to use as sender for notifications (optional, uses DEFAULT_FROM_EMAIL if not set)',
        blank=True,
        max_length=255
    )
    
    class Meta:
        verbose_name = 'Pardot Forms Settings'
    
    panels = [
        MultiFieldPanel(
            [
                FieldPanel('pardot_opt_in_form_url'),
                FieldPanel('pardot_contact_form_url'),
            ],
            heading='Pardot Form URLs',
            help_text='Configure the Pardot form handler URLs for each form type'
        ),
        MultiFieldPanel(
            [
                FieldPanel('contact_email_recipients'),
                FieldPanel('notification_from_email'),
            ],
            heading='Email Notifications',
            help_text='Configure email notification settings for contact form submissions'
        ),
    ]
    
    def get_email_recipients_list(self):
        """
        Parse the contact_email_recipients text field into a list of email addresses.
        
        Returns:
            list: List of email addresses, one per line (empty lines ignored)
        """
        if not self.contact_email_recipients:
            return []
        
        return [
            email.strip()
            for email in self.contact_email_recipients.splitlines()
            if email.strip()
        ]
    
    def __str__(self):
        return f'Pardot Forms Settings for {self.site}'
