from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submitted_at', 'first_name', 'last_name', 'email', 'company', 'phone', 'opt_in', 'sent_to_pardot', 'email_sent')
    list_filter = ('submitted_at', 'sent_to_pardot', 'email_sent')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'comments')
    readonly_fields = ('submitted_at', 'first_name', 'last_name', 'email', 'company', 'phone', 'opt_in', 'comments', 'sent_to_pardot', 'email_sent')
    date_hierarchy = 'submitted_at'
    
    def has_add_permission(self, request):
        # Prevent manual creation of submissions
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make all fields read-only
        return False
