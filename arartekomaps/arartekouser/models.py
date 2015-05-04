from django.db import models
from cssocialuser.models import CSAbstractSocialUser
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import UserManager

MEMBER_PHOTO_SLUG=getattr(settings,'PROFILE_PHOTO_DEFAULT_SLUG','no-profile-photo')


class ArartekoUser(CSAbstractSocialUser):
    is_editor = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now_add=True,editable=False)
    date_joined  = models.DateTimeField(auto_now_add=True,editable=False)

    objects = UserManager()

    def get_profile(self):
        return self

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_fullname(self):
        return self.fullname or self.username

    def __unicode__(self):
        return u'%s' % self.username

    class Meta:
        verbose_name = 'Ararteko erabiltzailea'
        verbose_name_plural = 'Ararteko erabiltzailea'