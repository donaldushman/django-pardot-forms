# Django Pardot Forms

Django app providing contact and subscription forms with Pardot integration and Bootstrap modal support.

Based on the WI-RECI project implementation.

## Features

- ✅ Contact form with Pardot integration
- ✅ Two-step subscription flow (email → full form with session)
- ✅ AJAX modal support for seamless UX
- ✅ Progressive enhancement (works without JavaScript)
- ✅ Database submission tracking with automatic 30-day cleanup
- ✅ Email notifications to staff
- ✅ Cloudflare Turnstile spam protection
- ✅ Honeypot field for additional spam filtering
- ✅ Accessibility compliant (ARIA labels, keyboard navigation)
- ✅ Read-only admin interface

## Installation

```bash
# Standard installation
pip install git+https://github.com/donaldushman/django-pardot-forms.git

# With Wagtail support
pip install git+https://github.com/donaldushman/django-pardot-forms.git[wagtail]
```

## Updating

To update to the latest version, use `--force-reinstall` and `--no-cache-dir` to ensure pip pulls fresh changes:

```bash
# Standard update
pip install --force-reinstall --no-cache-dir git+https://github.com/donaldushman/django-pardot-forms.git

# With Wagtail support
pip install --force-reinstall --no-cache-dir git+https://github.com/donaldushman/django-pardot-forms.git[wagtail]
```

> **Note:** Using `pip install --upgrade` alone may not fetch the latest changes due to pip's caching of git repositories.

## Quick Start

### 1. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'turnstile',  # Required for Turnstile captcha
    'pardot_forms',
]
```

### 2. Configure Settings

**Required settings:**

```python
# Pardot form handler URLs
PARDOT_CONTACT_FORM_URL = 'https://go.pardot.com/l/123456/contact-handler'
PARDOT_OPT_IN_FORM_URL = 'https://go.pardot.com/l/123456/opt-in-handler'

# Cloudflare Turnstile keys
TURNSTILE_SITE_KEY = 'your-turnstile-site-key'
TURNSTILE_SECRET_KEY = 'your-turnstile-secret-key'
```

**Optional settings:**

```python
# Email notification recipients (receives contact form submissions)
PARDOT_CONTACT_EMAIL_RECIPIENTS = ['admin@example.com', 'support@example.com']

# Email from address
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### 3. Include URLs

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('pardot_forms.urls')),
]
```

Available URLs:
- `/opt-in/` - Email subscription form (step 1)
- `/subscribe/` - Full subscription form (step 2)
- `/contact/` - Contact form
- `/contact-thank-you/` - Thank you page after contact submission
- `/subscribe-thank-you/` - Thank you page after subscription

### 4. Add Context Processor (Optional)

For a footer email form available site-wide:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                ...
                'pardot_forms.context_processors.footer_email_form',
            ],
        },
    },
]
```

Then in your footer template:

```html
<form id="footerEmailForm" method="post" action="{% url 'pardot_forms:email_form' %}">
    {% csrf_token %}
    {{ display_email_form }}
    <button type="submit">Subscribe</button>
</form>
```

### 5. Run Migrations

```bash
python manage.py migrate pardot_forms
```

### 6. Include Static Files

In your base template, include the pardot forms JavaScript:

```html
{% load static %}

<!-- Load Bootstrap first (required) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- Load pardot forms JavaScript -->
<script src="{% static 'pardot_forms/js/forms-modals.js' %}"></script>
```

Optional CSS for form styling:

```html
<link rel="stylesheet" href="{% static 'pardot_forms/css/forms.css' %}">
```

## Wagtail Integration

If you're using Wagtail CMS, you can manage Pardot form settings through the Wagtail admin interface instead of hardcoding them in your Django settings.

**📖 See the [Wagtail Integration Guide](docs/WAGTAIL.md) for complete documentation**  
**⚡ Quick start: [Wagtail Quick Reference](docs/WAGTAIL_QUICK_START.md)**

### Setup

1. **Ensure wagtail.contrib.settings is installed:**

```python
INSTALLED_APPS = [
    ...
    'wagtail.contrib.settings',  # Required for site settings
    'turnstile',
    'pardot_forms',
]
```

2. **Add the context processor:**

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                ...
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]
```

3. **Run migrations:**

```bash
python manage.py migrate pardot_forms
```

### Configure in Wagtail Admin

Navigate to **Settings > Pardot Forms** in the Wagtail admin and configure:

- **Subscription Form URL** - Your Pardot opt-in form handler URL
- **Contact Form URL** - Your Pardot contact form handler URL
- **Contact Form Email Recipients** - Email addresses to receive notifications (one per line)
- **Notification From Email** - Optional sender email address

### How It Works

The app automatically detects if Wagtail is available:
- **With Wagtail:** Settings from the Wagtail admin take priority, with Django settings as fallback
- **Without Wagtail:** Uses Django settings exclusively

This means you can:
- Configure settings per-site in multisite Wagtail installations
- Update URLs without redeploying code
- Allow non-technical staff to manage form configuration
- Still use Django settings as defaults or fallbacks

### Example

```python
# Django settings (fallback values)
PARDOT_CONTACT_FORM_URL = 'https://go.pardot.com/l/123456/contact-default'

# Wagtail admin settings (takes priority when set)
# Navigate to Settings > Pardot Forms and set:
# Contact Form URL: https://go.pardot.com/l/789012/contact-custom

# The app will use the Wagtail setting if available, otherwise the Django setting
```

## Usage

### Contact Modal

Add a contact modal to your page:

```html
<!-- Button to trigger modal -->
<button type="button" data-bs-toggle="modal" data-bs-target="#contactModal">
    Contact Us
</button>

<!-- Modal -->
<div class="modal fade" id="contactModal" tabindex="-1" aria-labelledby="contactModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="contactModalLabel">Contact Us</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div id="contactFormContainer"></div>
            </div>
        </div>
    </div>
</div>
```

### Subscribe Modal (Two-Step Flow)

```html
<!-- Subscribe Modal -->
<div class="modal fade" id="subscribeModal" tabindex="-1" aria-labelledby="subscribeModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="subscribeModalLabel">Subscribe</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div id="subscribeFormContainer"></div>
            </div>
        </div>
    </div>
</div>
```

### Standalone Forms

Link directly to the form pages:

```html
<a href="{% url 'pardot_forms:contact_form' %}">Contact Us</a>
<a href="{% url 'pardot_forms:email_form' %}">Subscribe</a>
```

## Management Commands

### Delete Old Submissions

Automatically clean up submissions older than 30 days:

```bash
# Dry run to see what would be deleted
python manage.py delete_old_submissions --dry-run

# Delete submissions older than 30 days (default)
python manage.py delete_old_submissions

# Delete submissions older than 90 days
python manage.py delete_old_submissions --days=90
```

Consider adding this to a cron job or scheduled task for automatic cleanup.

## Admin Interface

View submitted forms in Django admin at `/admin/pardot_forms/contactsubmission/`

The admin interface is read-only to preserve submission integrity. You can:
- View all submissions
- Search by name, email, or company
- Filter by date, Pardot status, or email status
- Export data using Django admin actions

## Development

### Testing

```bash
python -m pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .
```

## License

MIT License - see LICENSE file for details





