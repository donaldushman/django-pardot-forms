# Wagtail Integration Quick Reference

## Installation

```bash
pip install git+https://github.com/donaldushman/django-pardot-forms.git[wagtail]
```

## Setup (5 steps)

1. **Add to INSTALLED_APPS:**
   ```python
   INSTALLED_APPS = [
       ...
       'wagtail.contrib.settings',  # Required
       'turnstile',
       'pardot_forms',
   ]
   ```

2. **Add context processor:**
   ```python
   'context_processors': [
       ...
       'wagtail.contrib.settings.context_processors.settings',
   ]
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate pardot_forms
   ```

4. **Configure Turnstile:**
   ```python
   TURNSTILE_SITE_KEY = 'your-site-key'
   TURNSTILE_SECRET_KEY = 'your-secret-key'
   ```

5. **Configure in Wagtail admin:**
   - Go to **Settings > Pardot Forms**
   - Enter your form URLs and email recipients

## Settings Available in Wagtail Admin

| Setting | Description |
|---------|-------------|
| **Subscription Form URL** | Pardot handler URL for opt-in/subscription forms |
| **Contact Form URL** | Pardot handler URL for contact forms |
| **Contact Form Email Recipients** | Email addresses (one per line) to receive notifications |
| **Notification From Email** | Sender email for notifications (optional) |

## How It Works

```
Request comes in
    ↓
Check Wagtail settings for current site
    ↓
If set → Use Wagtail setting
If blank → Fall back to Django setting
If neither → Use default empty value
```

## Benefits

✅ Update URLs without code changes  
✅ Different settings per site (multisite)  
✅ Non-technical staff can manage  
✅ Still works without Wagtail  

## Multisite Example

```
Site A (brand-a.com)
- Contact URL: https://go.pardot.com/l/111111/...
- Recipients: team-a@example.com

Site B (brand-b.com)  
- Contact URL: https://go.pardot.com/l/222222/...
- Recipients: team-b@example.com
```

## Django Fallbacks (Optional)

Keep these in settings.py as defaults:

```python
PARDOT_CONTACT_FORM_URL = 'https://go.pardot.com/l/...'
PARDOT_OPT_IN_FORM_URL = 'https://go.pardot.com/l/...'
PARDOT_CONTACT_EMAIL_RECIPIENTS = ['admin@example.com']
```

## Need More Info?

See [Full Wagtail Documentation](./WAGTAIL.md) for:
- Detailed setup instructions
- Multisite configuration
- Troubleshooting guide
- Migration examples
- Best practices
