# Custom Forms Examples

This directory contains examples of how to extend `django-pardot-forms` with custom fields and functionality.

## Files Overview

- **`custom_forms.py`** - Example form classes extending `PardotContactForm`
- **`custom_views.py`** - Views to handle the custom forms
- **`custom_urls.py`** - URL configuration examples
- **`custom_contact_template.html`** - Example template with custom fields
- **`custom_models.py`** - Advanced example showing custom model extension

## Quick Start

### 1. Copy the Form Class

Copy the form class you want from `custom_forms.py` to your app's `forms.py`:

```python
from pardot_forms.forms import PardotContactForm

class CustomContactForm(PardotContactForm):
    phone = forms.CharField(max_length=20, required=False)
    company = forms.CharField(max_length=100, required=True)
    # ... add widget attributes
```

### 2. Create a View

Copy the corresponding view from `custom_views.py` to your `views.py`:

```python
from .forms import CustomContactForm
from pardot_forms.models import ContactSubmission

def custom_contact_view(request):
    # ... handle form submission
```

### 3. Add URL Pattern

Add the URL to your `urls.py`:

```python
path('custom-contact/', custom_views.custom_contact_view, name='custom_contact'),
```

### 4. Create Template

Use `custom_contact_template.html` as a starting point for your template.

## Approaches

### Simple: Store in Comments Field

The examples in `custom_views.py` show how to store custom field data in the existing `comments` field as JSON or formatted text. This is the simplest approach and doesn't require database changes.

**Pros:**
- No database migrations needed
- Works with existing model
- Easy to implement

**Cons:**
- Not queryable by custom fields
- Requires parsing JSON to access data

### Advanced: Custom Model

See `custom_models.py` for an example of extending the `ContactSubmission` model with custom fields.

**Pros:**
- Custom fields are queryable
- Proper data types and validation
- Better for reporting

**Cons:**
- Requires database migrations
- More complex setup

## Examples Included

### 1. CustomContactForm
Adds `phone` and `company` fields to the standard contact form.

### 2. JobApplicationForm
Example showing how to create a specialized form with:
- Position dropdown
- Resume URL field
- Custom validation

## Customization Tips

### Reordering Fields
Use `field_order` to control the display order:

```python
field_order = ['name', 'email', 'company', 'phone', 'comments', 'cf_turnstile_response']
```

### Custom Validation
Override `clean_<fieldname>()` or `clean()`:

```python
def clean_phone(self):
    phone = self.cleaned_data.get('phone', '')
    # Add validation logic
    return phone
```

### Conditional Required Fields
Make fields conditionally required:

```python
def clean(self):
    cleaned_data = super().clean()
    if some_condition:
        if not cleaned_data.get('phone'):
            raise ValidationError('Phone is required')
    return cleaned_data
```

### Bootstrap Styling
Add Bootstrap classes to widgets:

```python
widget=forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Enter your phone number'
})
```

## AJAX Support

All example views support AJAX requests. They check for the `X-Requested-With: XMLHttpRequest` header and return JSON responses:

```javascript
fetch('/custom-contact/', {
    method: 'POST',
    body: formData,
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Show success message
    }
});
```

## Need Help?

- Check the main README.md for basic setup
- See the django-pardot-forms source code for the base forms
- Django forms documentation: https://docs.djangoproject.com/en/stable/topics/forms/
