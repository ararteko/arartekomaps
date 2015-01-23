from django.db import models
from mptt.models import MPTTModelBase, MPTTModel

class Category(MPTTModel):

    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=255,unique=True, blank=True, null=True, help_text="Se actualiza al guardar")
       
    class MPTTMeta:
        order_insertion_by = ['name']
        parent_attr = 'parent'

    def get_absolute_url(self):
        return "/c/%s" % self.slug
    
    def get_node_slug(self):
        return self.slug
    
    def str2trans(self):
        return "cat_%s" % self.slug
        
    def icon(self):
        maincat = self
        while maincat.parent:
            maincat = maincat.parent
        return maincat.slug
        
    def __unicode__(self):
        return self.name