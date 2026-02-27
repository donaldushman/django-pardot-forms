from django.db import models
from django.utils import timezone


class ContactSubmission(models.Model):
    """
    Stores contact form submissions for 30 days before automatic cleanup.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=11, blank=True)
    company = models.CharField(max_length=100, blank=True)
    comments = models.TextField()
    opt_in = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)
    sent_to_pardot = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email} ({self.submitted_at.strftime('%Y-%m-%d %H:%M')})"
    
    @classmethod
    def delete_old_submissions(cls, days=30):
        """Delete submissions older than specified days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count, _ = cls.objects.filter(submitted_at__lt=cutoff_date).delete()
        return deleted_count
