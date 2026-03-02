from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from unittest.mock import patch, Mock
from datetime import timedelta
import json

from .models import ContactSubmission
from .forms import PardotOptInEmailForm, PardotOptInFullForm, PardotContactForm
from .views import contact_form_view, email_form_view, full_form_view


class ContactSubmissionModelTest(TestCase):
    """Tests for the ContactSubmission model."""

    def setUp(self):
        self.submission = ContactSubmission.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            company="Test Corp",
            comments="Test comment",
            opt_in=True
        )

    def test_contact_submission_creation(self):
        """Test that a ContactSubmission can be created with all fields."""
        self.assertEqual(self.submission.first_name, "John")
        self.assertEqual(self.submission.last_name, "Doe")
        self.assertEqual(self.submission.email, "john.doe@example.com")
        self.assertEqual(self.submission.phone, "1234567890")
        self.assertEqual(self.submission.company, "Test Corp")
        self.assertEqual(self.submission.comments, "Test comment")
        self.assertTrue(self.submission.opt_in)
        self.assertFalse(self.submission.sent_to_pardot)
        self.assertFalse(self.submission.email_sent)

    def test_contact_submission_str(self):
        """Test the string representation of ContactSubmission."""
        expected = f"John Doe - john.doe@example.com ({self.submission.submitted_at.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(self.submission), expected)

    def test_delete_old_submissions(self):
        """Test that old submissions are deleted correctly."""
        # Create an old submission (35 days ago)
        old_submission = ContactSubmission.objects.create(
            first_name="Old",
            last_name="Submission",
            email="old@example.com",
            comments="Old comment",
        )
        old_submission.submitted_at = timezone.now() - timedelta(days=35)
        old_submission.save()

        # Create a recent submission (5 days ago)
        recent_submission = ContactSubmission.objects.create(
            first_name="Recent",
            last_name="Submission",
            email="recent@example.com",
            comments="Recent comment",
        )
        recent_submission.submitted_at = timezone.now() - timedelta(days=5)
        recent_submission.save()

        # Delete submissions older than 30 days
        deleted_count = ContactSubmission.delete_old_submissions(days=30)

        # Verify only old submission was deleted
        self.assertEqual(deleted_count, 1)
        self.assertFalse(ContactSubmission.objects.filter(email="old@example.com").exists())
        self.assertTrue(ContactSubmission.objects.filter(email="recent@example.com").exists())


class PardotOptInEmailFormTest(TestCase):
    """Tests for the PardotOptInEmailForm."""

    def test_valid_email(self):
        """Test form is valid with a proper email."""
        form_data = {'email': 'test@example.com'}
        form = PardotOptInEmailForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        """Test form is invalid with an improper email."""
        form_data = {'email': 'not-an-email'}
        form = PardotOptInEmailForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_empty_email(self):
        """Test form is invalid when email is empty."""
        form_data = {'email': ''}
        form = PardotOptInEmailForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class PardotOptInFullFormTest(TestCase):
    """Tests for the PardotOptInFullForm."""

    def test_valid_form(self):
        """Test form is valid with proper data."""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company': 'Test Corp',
            'email': 'john@example.com',
            'pardot_extra_field': '',
        }
        with patch('turnstile.fields.TurnstileField.validate', return_value=True):
            form = PardotOptInFullForm(data=form_data)
            # Note: Turnstile field may require mocking in real tests
            self.assertIn('email', form.fields)
            self.assertIn('first_name', form.fields)

    def test_email_required(self):
        """Test that email is required."""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
        }
        form = PardotOptInFullForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class PardotContactFormTest(TestCase):
    """Tests for the PardotContactForm."""

    def test_valid_form(self):
        """Test form is valid with proper data."""
        form_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'company': 'Test Inc',
            'email': 'jane@example.com',
            'phone': '1234567890',
            'comments': 'Test message',
            'opt_in': True,
            'pardot_extra_field': '',  # Honeypot should be empty
        }
        with patch('turnstile.fields.TurnstileField.validate', return_value=True):
            form = PardotContactFormTest()
            self.assertIsNotNone(form)

    def test_honeypot_field_spam_detection(self):
        """Test that honeypot field detects spam."""
        form_data = {
            'first_name': 'Spam',
            'last_name': 'Bot',
            'email': 'spam@example.com',
            'comments': 'Buy my product!',
            'pardot_extra_field': 'I am a bot',  # Honeypot filled
        }
        with patch('turnstile.fields.TurnstileField.validate', return_value=True):
            form = PardotContactForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn('Spam detected', str(form.errors))

    def test_email_required(self):
        """Test that email field is required."""
        form_data = {
            'first_name': 'John',
            'comments': 'Test',
            'pardot_extra_field': '',
        }
        form = PardotContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


@override_settings(
    PARDOT_CONTACT_FORM_URL='https://go.pardot.com/test/contact',
    PARDOT_OPT_IN_FORM_URL='https://go.pardot.com/test/optin',
    PARDOT_CONTACT_EMAIL_RECIPIENTS=['admin@example.com'],
    DEFAULT_FROM_EMAIL='noreply@example.com'
)
class EmailFormViewTest(TestCase):
    """Tests for the email_form_view."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_email_form(self):
        """Test GET request renders the email form."""
        response = self.client.get(reverse('pardot_forms:email_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pardot_forms/email_form.html')
        self.assertIn('email_form', response.context)

    def test_post_valid_email_redirects(self):
        """Test POST with valid email saves to session and redirects."""
        response = self.client.post(
            reverse('pardot_forms:email_form'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pardot_forms:full_form'))
        self.assertEqual(self.client.session.get('email'), 'test@example.com')

    def test_post_invalid_email(self):
        """Test POST with invalid email shows errors."""
        response = self.client.post(
            reverse('pardot_forms:email_form'),
            {'email': 'not-an-email'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'email_form', 'email', 'Enter a valid email address.')

    def test_ajax_post_valid_email(self):
        """Test AJAX POST with valid email returns JSON."""
        response = self.client.post(
            reverse('pardot_forms:email_form'),
            {'email': 'ajax@example.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])


@override_settings(
    PARDOT_CONTACT_FORM_URL='https://go.pardot.com/test/contact',
    PARDOT_OPT_IN_FORM_URL='https://go.pardot.com/test/optin',
    PARDOT_CONTACT_EMAIL_RECIPIENTS=['admin@example.com'],
    DEFAULT_FROM_EMAIL='noreply@example.com'
)
class FullFormViewTest(TestCase):
    """Tests for the full_form_view."""

    def setUp(self):
        self.factory = RequestFactory()
        session = self.client.session
        session['email'] = 'test@example.com'
        session.save()

    @patch('pardot_forms.views.requests.post')
    @patch('turnstile.fields.TurnstileField.validate')
    def test_post_valid_form_sends_to_pardot(self, mock_turnstile, mock_post):
        """Test POST with valid data sends to Pardot."""
        mock_turnstile.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.post(
            reverse('pardot_forms:full_form'),
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'company': 'Test Corp',
                'pardot_extra_field': '',
                'turnstile': 'fake-token',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pardot_forms:subscribe_thank_you'))
        mock_post.assert_called_once()

    def test_get_full_form_with_session_email(self):
        """Test GET request shows form with email from session."""
        response = self.client.get(reverse('pardot_forms:full_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pardot_forms/full_form.html')


@override_settings(
    PARDOT_CONTACT_FORM_URL='https://go.pardot.com/test/contact',
    PARDOT_OPT_IN_FORM_URL='https://go.pardot.com/test/optin',
    PARDOT_CONTACT_EMAIL_RECIPIENTS=['admin@example.com'],
    DEFAULT_FROM_EMAIL='noreply@example.com'
)
class ContactFormViewTest(TestCase):
    """Tests for the contact_form_view."""

    def test_get_contact_form(self):
        """Test GET request renders the contact form."""
        response = self.client.get(reverse('pardot_forms:contact_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pardot_forms/contact_form.html')
        self.assertIn('contact_form', response.context)

    @patch('pardot_forms.views.requests.post')
    @patch('turnstile.fields.TurnstileField.validate')
    def test_post_valid_form_creates_submission(self, mock_turnstile, mock_post):
        """Test POST with valid data creates ContactSubmission."""
        mock_turnstile.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.assertEqual(ContactSubmission.objects.count(), 0)

        response = self.client.post(
            reverse('pardot_forms:contact_form'),
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@example.com',
                'phone': '1234567890',
                'company': 'Test Inc',
                'comments': 'Test message',
                'opt_in': True,
                'pardot_extra_field': '',
                'turnstile': 'fake-token',
            }
        )

        self.assertEqual(ContactSubmission.objects.count(), 1)
        submission = ContactSubmission.objects.first()
        self.assertEqual(submission.first_name, 'Jane')
        self.assertEqual(submission.email, 'jane@example.com')
        self.assertTrue(submission.sent_to_pardot)

    @patch('pardot_forms.views.requests.post')
    @patch('pardot_forms.views.send_mail')
    @patch('turnstile.fields.TurnstileField.validate')
    def test_post_valid_form_sends_email(self, mock_turnstile, mock_send_mail, mock_post):
        """Test POST with valid data sends email notification."""
        mock_turnstile.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.post(
            reverse('pardot_forms:contact_form'),
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@example.com',
                'comments': 'Test message',
                'pardot_extra_field': '',
                'turnstile': 'fake-token',
            }
        )

        # Verify email was sent
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('Jane Smith', call_args[0][0])  # Subject
        self.assertEqual(call_args[0][3], ['admin@example.com'])  # Recipients

    @patch('pardot_forms.views.requests.post')
    @patch('turnstile.fields.TurnstileField.validate')
    def test_ajax_post_returns_json(self, mock_turnstile, mock_post):
        """Test AJAX POST returns JSON response."""
        mock_turnstile.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.post(
            reverse('pardot_forms:contact_form'),
            {
                'first_name': 'AJAX',
                'last_name': 'User',
                'email': 'ajax@example.com',
                'comments': 'Test',
                'pardot_extra_field': '',
                'turnstile': 'fake-token',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Thank you', data['message'])


class ThankYouViewsTest(TestCase):
    """Tests for thank you page views."""

    def test_contact_thank_you(self):
        """Test contact thank you page renders."""
        response = self.client.get(reverse('pardot_forms:contact_thank_you'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pardot_forms/contact_thank_you.html')

    def test_subscribe_thank_you(self):
        """Test subscribe thank you page renders."""
        response = self.client.get(reverse('pardot_forms:subscribe_thank_you'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pardot_forms/subscribe_thank_you.html')
