"""
Example: Advanced approach using a custom model

This shows how to create a custom model that extends ContactSubmission
to store additional fields in dedicated database columns.

Note: This requires creating and running migrations in your project.
"""

from django.db import models
from pardot_forms.models import ContactSubmission


class ExtendedContactSubmission(ContactSubmission):
    """
    Extended model with additional fields.
    
    This creates a separate table with a OneToOne relationship to ContactSubmission,
    allowing you to store custom fields while keeping the base pardot_forms intact.
    """
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Extended Contact Submission'
        verbose_name_plural = 'Extended Contact Submissions'
    
    def __str__(self):
        return f"{self.name} - {self.company}"


class JobApplication(ContactSubmission):
    """
    Job application with position and resume fields.
    """
    POSITION_CHOICES = [
        ('engineer', 'Software Engineer'),
        ('designer', 'UX Designer'),
        ('manager', 'Product Manager'),
    ]
    
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    resume_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
    
    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"


# Alternative approach: Separate model with ForeignKey
class CustomField(models.Model):
    """
    Store custom fields as key-value pairs.
    
    This is the most flexible approach but requires more complex queries.
    """
    submission = models.ForeignKey(
        ContactSubmission,
        on_delete=models.CASCADE,
        related_name='custom_fields'
    )
    field_name = models.CharField(max_length=100)
    field_value = models.TextField()
    
    class Meta:
        verbose_name = 'Custom Field'
        verbose_name_plural = 'Custom Fields'
        unique_together = ['submission', 'field_name']
    
    def __str__(self):
        return f"{self.submission.name} - {self.field_name}"


# Example view using the extended model:
"""
from .models import ExtendedContactSubmission
from .forms import CustomContactForm

def custom_contact_view(request):
    if request.method == 'POST':
        form = CustomContactForm(request.POST)
        if form.is_valid():
            submission = ExtendedContactSubmission.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                comments=form.cleaned_data['comments'],
                phone=form.cleaned_data['phone'],
                company=form.cleaned_data['company'],
                opt_in=False
            )
            # ... handle email notification
            return JsonResponse({'success': True})
"""


# Example admin configuration:
"""
from django.contrib import admin
from .models import ExtendedContactSubmission, JobApplication

@admin.register(ExtendedContactSubmission)
class ExtendedContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'phone', 'submitted_at']
    list_filter = ['submitted_at', 'email_sent']
    search_fields = ['name', 'email', 'company', 'phone']
    readonly_fields = ['submitted_at']
    date_hierarchy = 'submitted_at'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'position', 'submitted_at']
    list_filter = ['position', 'submitted_at']
    search_fields = ['name', 'email']
"""
