from django.urls import path
from . import views

app_name = 'pardot_forms'

urlpatterns = [
    path("opt-in/", views.email_form_view, name='email_form'),
    path("subscribe/", views.full_form_view, name='full_form'),
    path("contact/", views.contact_form_view, name='contact_form'),
    path("contact-thank-you/", views.contact_thank_you, name='contact_thank_you'),
    path("subscribe-thank-you/", views.subscribe_thank_you, name='subscribe_thank_you'),
]
