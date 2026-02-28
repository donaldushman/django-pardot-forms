# Generated migration for Wagtail settings

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pardot_forms', '0001_initial'),
        ('wagtailcore', '__latest__'),
    ]

    operations = [
        migrations.CreateModel(
            name='PardotFormsSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pardot_opt_in_form_url', models.URLField(blank=True, help_text='Pardot URL for the opt-in/subscription form', max_length=500, verbose_name='Subscription Form URL')),
                ('pardot_contact_form_url', models.URLField(blank=True, help_text='Pardot URL for the contact form', max_length=500, verbose_name='Contact Form URL')),
                ('contact_email_recipients', models.TextField(blank=True, help_text='Email addresses to receive contact form notifications (one per line)', verbose_name='Contact Form Email Recipients')),
                ('notification_from_email', models.EmailField(blank=True, help_text='Email address to use as sender for notifications (optional, uses DEFAULT_FROM_EMAIL if not set)', max_length=255, verbose_name='Notification From Email')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site')),
            ],
            options={
                'verbose_name': 'Pardot Forms Settings',
                'abstract': False,
            },
        ),
    ]
