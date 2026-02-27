# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-27

### Added
- Initial release based on WI-RECI project implementation
- Contact form with Pardot integration
- Two-step subscription flow (email → full form with session)
- AJAX modal support for seamless UX
- Progressive enhancement (works without JavaScript)
- Database submission tracking with automatic 30-day cleanup
- Email notifications to staff on contact form submissions
- Cloudflare Turnstile spam protection
- Honeypot field for additional spam filtering
- Accessibility features (ARIA labels, keyboard navigation, screen reader support)
- Read-only admin interface for viewing submissions
- Management command for cleaning up old submissions
- Bootstrap 5 compatible templates
- Comprehensive documentation

### Features
- `ContactSubmission` model to track all form submissions
- Three form types: 
  - `PardotOptInEmailForm` - Simple email capture
  - `PardotOptInFullForm` - Full subscription form
  - `PardotContactForm` - Complete contact form with all fields
- Context processor for footer email form
- URL routing for all form views and thank you pages
- Static files (CSS and JavaScript) for enhanced UX

### Technical Details
- Django 4.0+ compatible
- Python 3.8+ compatible
- Uses django-turnstile for Cloudflare Turnstile integration
- Bootstrap 5 for UI components
- AJAX-powered modal forms with graceful degradation
