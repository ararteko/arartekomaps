from django.db import models
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    User = settings.AUTH_USER_MODEL
except ImportError:
    from django.contrib.auth.models import User
from photologue.models import Photo
from arartekomaps.places.models import Place
from arartekomaps.utils.slug import *
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail

class Comment(models.Model):
    """ """

    slug = models.BigIntegerField(unique=True, db_index=True, editable=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    parent = models.ForeignKey(Place, null=True, blank=True, related_name='parent')
    body = models.TextField(null=True, blank=True)
    photo = models.ForeignKey(Photo, null=True, blank=True)

    is_public = models.BooleanField(default=True, db_index=True)
    # ALTER TABLE `mycomment_comment` ADD `is_deleted` BOOLEAN NOT NULL DEFAULT FALSE AFTER `is_public` ;
    is_deleted = models.BooleanField(default=False, db_index=True)
    public_date = models.DateTimeField(db_index=True)

    ip_address = models.IPAddressField('IP address', blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    def get_absolute_url(self):
        """ """
        return '%s#c%d' % (self.parent.get_absolute_url(), self.slug)

    def save(self, *args, **kwargs):
        """ """

        if not self.slug:
            self.slug = time_slug()

        super(Comment, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-added']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(_('[NEW COMMENT] '), _('New comment saved: ') + instance.body + '\n\n' + settings.HOST+'/admin/mycomment/comment/' + str(instance.id), settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_NOTIFICATION], fail_silently=True)
    return True

post_save.connect(send_comment_notification, sender=Comment)

