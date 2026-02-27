"""
Example: URL configuration for custom forms

Add these patterns to your project's urls.py
"""

from django.urls import path, include
from . import custom_views

urlpatterns = [
    # Include the standard pardot_forms URLs
    path('forms/', include('pardot_forms.urls')),
    
    # Add your custom form URLs
    path('custom-contact/', custom_views.custom_contact_view, name='custom_contact'),
    path('apply/', custom_views.job_application_view, name='job_application'),
]
