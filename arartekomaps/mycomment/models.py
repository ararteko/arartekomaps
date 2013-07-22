from django.db import models
from django.contrib.auth.models import User
from photologue.models import Photo
from arartekomaps.places.models import Place
from arartekomaps.utils.slug import *
from django.db.models.signals import post_save

class Comment(models.Model):
    """ """

    slug = models.BigIntegerField(unique=True,db_index=True,editable=False)

    author = models.ForeignKey(User)

    parent = models.ForeignKey(Place,null = True, blank=True, related_name='parent')
    body = models.TextField(null=True,blank = True)
    photo = models.ForeignKey(Photo,null=True, blank=True)

    is_public = models.BooleanField(default = True, db_index=True)
    public_date = models.DateTimeField(db_index=True)

    ip_address  = models.IPAddressField('IP address', blank=True, null=True)    
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)   
        
    
    def get_absolute_url(self):
        """ """
        return '%s#c%d' % (self.parent.get_absolute_url(),self.slug)    
    
    def save(self, *args, **kwargs):
        """ """
         
        if not self.slug:
            self.slug = time_slug()

        super(Comment, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-added']
        verbose_name = 'Erantzuna'        
        verbose_name_plural = 'Erantzunak'


def send_comment_notification(sender, comment, **kwargs):
    if comment:
        send_mail('[IRUZKIN BERRIA] ', 'Iruzkin berri bat gorde da: '+comment.body+'\n\n'+settings.HOST+'/admin/mycomment/comment/' + str(comment.id), DEFAULT_FROM_EMAIL,
            [EMAIL_NOTIFICATION], fail_silently=True)   
    return True

#post_save.connect(send_comment_notification, sender=Comment)
        
