# Wagtail Integration Guide

This guide covers using `django-pardot-forms` with Wagtail CMS.

## Why Use Wagtail Integration?

The Wagtail integration allows you to:

- **Configure form URLs** through the Wagtail admin interface instead of code
- **Manage email recipients** without redeploying
- **Per-site configuration** in multisite Wagtail installations
- **Non-technical staff** can update settings without touching code
- **Django settings fallback** for defaults or when Wagtail is not available

## Installation

Install with Wagtail support:

```bash
pip install git+https://github.com/donaldushman/django-pardot-forms.git[wagtail]
```

## Setup

### 1. Configure Django Settings

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Wagtail apps
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    
    'wagtail.contrib.settings',  # Required for site settings
    'modelcluster',
    'taggit',
    
    # Third-party apps
    'turnstile',
    
    # Your apps
    'pardot_forms',  # Must come after wagtail.contrib.settings
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',  # Required
            ],
        },
    },
]

# Cloudflare Turnstile (required)
TURNSTILE_SITE_KEY = 'your-turnstile-site-key'
TURNSTILE_SECRET_KEY = 'your-turnstile-secret-key'

# Optional: Django settings fallbacks
PARDOT_CONTACT_FORM_URL = 'https://go.pardot.com/l/123456/contact-default'
PARDOT_OPT_IN_FORM_URL = 'https://go.pardot.com/l/123456/optin-default'
PARDOT_CONTACT_EMAIL_RECIPIENTS = ['fallback@example.com']
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### 2. Run Migrations

```bash
python manage.py migrate pardot_forms
```

The migration will create the `pardot_forms_pardotformssettings` table.

### 3. Access Wagtail Admin Settings

1. Log into Wagtail admin
2. Navigate to **Settings** in the sidebar
3. Click **Pardot Forms**
4. Configure your settings

## Configuration Options

### Subscription Form URL

**Field:** `pardot_opt_in_form_url`

The Pardot form handler URL for subscription/opt-in forms.

Example: `https://go.pardot.com/l/123456/2024-02-01/abcdef`

### Contact Form URL

**Field:** `pardot_contact_form_url`

The Pardot form handler URL for contact forms.

Example: `https://go.pardot.com/l/123456/2024-02-01/xyz123`

### Contact Form Email Recipients

**Field:** `contact_email_recipients`

Email addresses to receive contact form notifications. Enter one email address per line.

Example:
```
sales@example.com
support@example.com
admin@example.com
```

### Notification From Email

**Field:** `notification_from_email`

The sender email address for notification emails. If left blank, uses `DEFAULT_FROM_EMAIL` from Django settings.

Example: `noreply@example.com`

## How Settings Resolution Works

The app uses a cascading priority system:

1. **Wagtail Settings** (highest priority) - From Wagtail admin if set
2. **Django Settings** (fallback) - From `settings.py`
3. **Default Values** (last resort) - Empty strings or empty lists

This means:
- Set defaults in Django settings for all sites
- Override per-site using Wagtail admin
- Non-technical staff can update URLs without code changes

### Example: Settings Resolution

```python
# In settings.py (fallback)
PARDOT_CONTACT_FORM_URL = 'https://go.pardot.com/l/123456/contact-default'

# In Wagtail admin for site1.example.com
# Contact Form URL: https://go.pardot.com/l/789012/contact-site1

# In Wagtail admin for site2.example.com
# Contact Form URL: (left blank)

# Result:
# - Requests on site1.example.com use: "...contact-site1"
# - Requests on site2.example.com use: "...contact-default" (Django fallback)
```

## Multisite Configuration

In multisite Wagtail installations, each site can have its own Pardot form settings.

### Setup for Multiple Sites

1. Configure your default site in Wagtail: **Settings > Sites**
2. For each site, navigate to **Settings > Pardot Forms**
3. The settings panel will show which site you're configuring
4. Each site can have different Pardot URLs and email recipients

### Use Case: Multiple Brands

```
Site 1: brand-a.com
  - Subscription URL: https://go.pardot.com/l/111111/...
  - Contact URL: https://go.pardot.com/l/111111/...
  - Recipients: branda-team@example.com

Site 2: brand-b.com
  - Subscription URL: https://go.pardot.com/l/222222/...
  - Contact URL: https://go.pardot.com/l/222222/...
  - Recipients: brandb-team@example.com

Site 3: blog.brand-a.com
  - (Settings left blank, uses Django fallbacks)
```

## Accessing Settings in Code

If you need to access the Pardot settings in your own code:

```python
from pardot_forms.wagtail_hooks import PardotFormsSettings

def my_view(request):
    # Get settings for the current request's site
    settings = PardotFormsSettings.for_request(request)
    
    # Access individual settings
    contact_url = settings.pardot_contact_form_url
    email_recipients = settings.get_email_recipients_list()
    
    # Or get settings for a specific site
    from wagtail.models import Site
    site = Site.objects.get(hostname='example.com')
    settings = PardotFormsSettings.for_site(site)
```

## Templates

You can access Pardot settings in templates using the Wagtail settings tag:

```django
{% load wagtailsettings_tags %}
{% get_settings %}

<!-- Access settings -->
{{ settings.pardot_forms.PardotFormsSettings.pardot_contact_form_url }}
{{ settings.pardot_forms.PardotFormsSettings.notification_from_email }}
```

## Troubleshooting

### Settings Not Appearing in Wagtail Admin

**Issue:** The Pardot Forms settings don't appear in the Wagtail admin Settings menu.

**Solutions:**

1. Verify `wagtail.contrib.settings` is in `INSTALLED_APPS`
2. Ensure `pardot_forms` comes **after** `wagtail.contrib.settings`
3. Run migrations: `python manage.py migrate pardot_forms`
4. Clear cache: `python manage.py clear_cache` (if using cache)
5. Restart the development server

### Settings Not Being Used

**Issue:** Forms still use Django settings instead of Wagtail settings.

**Solutions:**

1. Check that settings are saved in Wagtail admin (not blank)
2. Verify the request is for the correct site
3. Check that the context processor is configured:
   ```python
   'wagtail.contrib.settings.context_processors.settings',
   ```
4. Ensure you're using the latest migration (0002_pardotformssettings)

### Multisite Settings Conflict

**Issue:** Wrong site settings being used on a multisite installation.

**Solutions:**

1. Verify sites are configured correctly in **Settings > Sites**
2. Check that each site has a unique hostname/port
3. Ensure `WAGTAIL_SITE_NAME` is not hardcoded
4. Use Site.find_for_request() to debug which site is matched:
   ```python
   from wagtail.models import Site
   site = Site.find_for_request(request)
   print(f"Current site: {site.site_name} ({site.hostname})")
   ```

## Migration Notes

### From Django Settings to Wagtail Settings

If you're migrating from hardcoded Django settings:

1. **Keep your Django settings** - They serve as fallbacks
2. **Install the Wagtail integration** - Add wagtail.contrib.settings
3. **Run migrations** - `python manage.py migrate pardot_forms`
4. **Copy values to Wagtail admin** - Transfer URLs and emails
5. **Test thoroughly** - Ensure forms still work
6. **Optional: Remove Django settings** - Once confident, you can remove the hardcoded values

### Data Migration Example

If you want to automatically populate Wagtail settings from Django settings:

```python
# Create a data migration
# python manage.py makemigrations pardot_forms --empty --name populate_wagtail_settings

from django.db import migrations
from django.conf import settings

def populate_wagtail_settings(apps, schema_editor):
    try:
        Site = apps.get_model('wagtailcore', 'Site')
        PardotFormsSettings = apps.get_model('pardot_forms', 'PardotFormsSettings')
        
        # Get the default site
        default_site = Site.objects.filter(is_default_site=True).first()
        if not default_site:
            return
        
        # Create or update settings
        pardot_settings, created = PardotFormsSettings.objects.get_or_create(
            site=default_site,
            defaults={
                'pardot_opt_in_form_url': getattr(settings, 'PARDOT_OPT_IN_FORM_URL', ''),
                'pardot_contact_form_url': getattr(settings, 'PARDOT_CONTACT_FORM_URL', ''),
                'contact_email_recipients': '\n'.join(
                    getattr(settings, 'PARDOT_CONTACT_EMAIL_RECIPIENTS', [])
                ),
                'notification_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
            }
        )
    except Exception as e:
        print(f"Could not populate Wagtail settings: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('pardot_forms', '0002_pardotformssettings'),
        ('wagtailcore', '__latest__'),
    ]
    
    operations = [
        migrations.RunPython(populate_wagtail_settings, migrations.RunPython.noop),
    ]
```

## Best Practices

### Security

1. **Restrict Admin Access** - Only give Pardot settings access to trusted staff
2. **Use HTTPS** - Always use HTTPS for Pardot URLs
3. **Validate Recipients** - Double-check email recipient addresses
4. **Monitor Logs** - Watch for failed Pardot submissions

### Performance

1. **Cache Settings** - Wagtail automatically caches site settings
2. **Use select_related** - If querying settings frequently
3. **Avoid Template Loading** - Don't load settings in templates repeatedly

### Maintenance

1. **Document URLs** - Keep a record of which Pardot forms map to which URLs
2. **Test After Changes** - Always test forms after updating URLs
3. **Use Fallbacks** - Keep Django settings as fallbacks
4. **Version Control** - Track changes to Django settings in git

## Additional Resources

- [Wagtail Settings Documentation](https://docs.wagtail.org/en/stable/reference/contrib/settings.html)
- [Pardot Form Handlers](https://help.salesforce.com/s/articleView?id=sf.pardot_forms.htm)
- [django-pardot-forms README](../README.md)

## Support

For issues specific to Wagtail integration:
1. Check this guide's troubleshooting section
2. Verify Wagtail and dependencies are up to date
3. Check the django-pardot-forms GitHub issues
4. Test with Django settings fallback to isolate the issue
