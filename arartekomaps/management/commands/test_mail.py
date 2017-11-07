from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

DEFAULT_FROM_EMAIL = getattr(settings,'DEFAULT_FROM_EMAIL', '')

EMAIL_HOST = getattr(settings,'EMAIL_HOST', '')
EMAIL_HOST_USER = getattr(settings,'EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = getattr(settings,'EMAIL_HOST_PASSWORD', '')

class Command(BaseCommand):
    args = ''
    help = 'Test email server'
    
    def handle(self, *args, **options):
        send_mail('Testing email', 'If you receive this message, everything is all right', 
            DEFAULT_FROM_EMAIL, ['uodriozola@codesyntax.com'], fail_silently=False)
    
