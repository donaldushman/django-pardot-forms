from django.core.management.base import BaseCommand
from pardot_forms.models import ContactSubmission


class Command(BaseCommand):
    help = 'Delete contact submissions older than specified number of days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete submissions older than this many days (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            from django.utils import timezone
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            old_submissions = ContactSubmission.objects.filter(submitted_at__lt=cutoff_date)
            count = old_submissions.count()
            
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} submissions older than {days} days '
                    f'(before {cutoff_date.strftime("%Y-%m-%d")})'
                )
            )
            if count > 0:
                self.stdout.write('\nFirst 10 submissions that would be deleted:')
                for submission in old_submissions[:10]:
                    self.stdout.write(f'  - {submission}')
        else:
            deleted_count = ContactSubmission.delete_old_submissions(days=days)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} submissions older than {days} days'
                )
            )
