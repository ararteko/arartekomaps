#* - encoding: utf-8 -*
from django.db import models
from utils import slugify
from django.db.models.signals import pre_save


class Location(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child_set')
    slug = models.SlugField(blank=True)
    level = models.IntegerField()
    lat = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    lon = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)

    class Meta:
        verbose_name_plural = ('locations')
        unique_together = ('parent', 'name')

    def __repr__(self):
        return '<Location %s>' % self

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        if self.level==0:
            return "/l/"
        elif self.level==1:
            return "/l/%s/" % self.slug
        elif self.level==2:
            return "/l/%s/%s/" % (self.parent.slug,self.slug)
        else:
            return '/bad_url/'

    def save(self):
        super( Location, self ).save()

def generate_location_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_proposal = slugify(u'%s' % (instance.name))
        prev_slug = Location.objects.filter(slug__startswith=slug_proposal)
        if prev_slug:
            slug_proposal += u'-%s' % len(prev_slug)
        instance.slug = slug_proposal

def generate_location_level(sender, instance, **kwargs):
    if instance.parent:
        instance.level=instance.parent.level+1
    else:
        instance.level=0

pre_save.connect(generate_location_slug, sender=Location)
pre_save.connect(generate_location_level, sender=Location)
