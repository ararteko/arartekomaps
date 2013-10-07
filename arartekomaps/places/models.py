#* - encoding: utf-8 -*
from django.db import models
from utils import slugify
from django.db.models.signals import pre_save
from arartekomaps.locations.models import Location
from arartekomaps.categories.models import Category
from photologue.models import ImageModel
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Count
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save

DEFAULT_FROM_EMAIL = getattr(settings,'DEFAULT_FROM_EMAIL', '')
EMAIL_NOTIFICATION = getattr(settings,'EMAIL_NOTIFICATION', '')

ACCESS_CHOICES = (
        ('a', 'Accesible'),
        ('p', 'Practicable'),
        ('n', 'No accesible'),
        ('s', 'Sin datos'),
    )


class Place(models.Model):
    slug=models.SlugField(max_length=255, blank=True, null=True, unique=True, help_text="Sí está vacio se actualiza al guardar")
    name=models.CharField(max_length=255, verbose_name='Nombre')
    category=models.ForeignKey(Category, verbose_name='Categoría')
    description =models.TextField(null=True, blank=True, verbose_name=u'Descripción')        
    address1=models.CharField(max_length=100, blank=True, verbose_name='Dirección 1')
    address2=models.CharField(max_length=100, blank=True, verbose_name='Dirección 2')
    postalcode=models.CharField(max_length=5, blank=True, verbose_name='Codigo postal')
    city=models.ForeignKey(Location, verbose_name='Municipio')
    locality=models.CharField(max_length=100, blank=True, verbose_name='Localidad')
    source=models.CharField(max_length=20, blank=True, verbose_name='Codigo entidad')
    source_id=models.CharField(max_length=20, blank=True, verbose_name='Codigo origen')
    lat=models.DecimalField(max_digits=12, decimal_places=8,null=True,blank=True)
    lon=models.DecimalField(max_digits=12, decimal_places=8,null=True,blank=True)
    tlf=models.CharField(max_length=30, blank=True, verbose_name='Telefono')
    fax=models.CharField(max_length=15, blank=True, verbose_name='Fax')
    url=models.CharField(max_length=255, blank=True, verbose_name='URL')
    email=models.CharField(max_length=255, blank=True, verbose_name='Email')
    
    def get_comments_count(self):
        return self.parent.all().count()

    def access_list(self):
        if self.access.count()>0:
            access = self.access.all()[0]
            access_tuple = (
            ('aphysic', access.aphysic, _('aphysic'), _("access_%s" % access.aphysic)),
            ('avisual', access.avisual, _('avisual'), _("access_%s" % access.avisual)),
            ('aaudio', access.aaudio, _('aaudio'), _("access_%s" % access.aaudio)),
            ('aintelec', access.aintelec, _('aintelec'), _("access_%s" % access.aintelec)),
            ('aorganic', access.aorganic, _('aorganic'), _("access_%s" % access.aorganic))
            )
        else:
            access_tuple = ()
        return access_tuple

    def access_dict_list(self):
        if self.access.count()>0:
            access = self.access.all()[0]
            acc = dict(ACCESS_CHOICES)
            access_dict = {
                'aphysic': acc[access.aphysic],
                'avisual': acc[access.avisual],
                'aaudio': acc[access.aaudio],
                'aintelec': acc[access.aintelec],
                'aorganic': acc[access.aorganic]
            }
        else:
            access_dict = {}
        return access_dict

    def access_data(self):
        if self.access.count()==1:
            access = self.access.all()[0]
            access_dict = {'description': access.description or '', 'fileurl': access.fileurl or '',
                            'aphysic':access.aphysic, 'avisual':access.avisual, 'aaudio':access.aaudio,
                            'aintelec':access.aintelec, 'avisual':access.aorganic}
            return access_dict

    def biblio_data(self):
        if self.biblio.count()==1:
            biblio = self.biblio.all()[0]
            return biblio
        else:
            return
            
    def get_places_within_25 (self):
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute("""SELECT id, ( 
        3959 * acos( cos( radians(37) ) * cos( radians( lat ) ) * 
        cos( radians( lon ) - radians(-122) ) + sin( radians(37) ) * 
        sin( radians( lat ) ) ) )
        AS distance FROM places_place HAVING distance < 25000
        ORDER BY distance LIMIT 0 , 10;""")
        ids = [row[0] for row in cursor.fetchall()]

        return Place.objects.filter(id__in=ids)
        
    def nearby_locations(self, radius=2, max_results=10, use_miles=False):
        latitude = self.lat
        longitude =self.lon
        if use_miles:
            distance_unit = 3959
        else:
            distance_unit = 6371

        from django.db import connection, transaction
        cursor = connection.cursor()

        sql = """SELECT id, (%f * acos( cos( radians(%f) ) * cos( radians( lat ) ) *
        cos( radians( lon ) - radians(%f) ) + sin( radians(%f) ) * sin( radians( lat ) ) ) )
        AS distance FROM places_place HAVING distance < %d
        ORDER BY distance LIMIT 0 , %d;""" % (distance_unit, latitude, longitude, latitude, int(radius), max_results)
        cursor.execute(sql)

        dist_dict = {}
        for row in cursor.fetchall():
            k, v = row[0], row[1]
            dist_dict[k] = v
        ids = dist_dict.keys()
        objs = Place.objects.filter(id__in=ids)
        all_objs = [(int(dist_dict[obj.id]*1000),obj) for obj in objs]
        all_objs.sort()
        return all_objs[1:]
                   
    def icon(self):
        return self.category.icon()
        
    def get_absolute_url(self):
        return "/p/%s/" % (self.slug)

    def __unicode__(self):
        return self.name


class Access(models.Model):   
    aphysic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name='Física')
    avisual = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name='Visual')
    aaudio = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name='Audio')
    aintelec = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name='Intelectual')
    aorganic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name='Orgánica')
    description = models.TextField(null=True, blank=True, verbose_name='Descripción')
    fileurl = models.TextField(null=True, blank=True, verbose_name='URL ficha')
    place = models.ForeignKey(Place, unique=True, verbose_name='Place', related_name='access')

class Bibtopic(models.Model):
    """ """
    name = models.CharField(max_length=50, verbose_name='Nombre')
    
    def __unicode__(self):
        return self.name

class Bibservice(models.Model):
    """ """
    name = models.CharField(max_length=50, verbose_name='Nombre')
    
    def __unicode__(self):
        return self.name
    
class Biblio(models.Model):
    """ """
    BTYPE_CHOICES = (
        ('p', 'Publico'),
        ('r', 'Privado'),
        ('i', 'Infantil'),
        ('v', 'Investigacion'),
        ('t', 'Patrimonial'),
        ('e', 'Especializada')
    )
    btype = models.CharField(max_length=1, choices=BTYPE_CHOICES, blank=True, verbose_name='Tipo')   
    start_year = models.DecimalField(max_digits=4, decimal_places=0,null=True,blank=True, verbose_name='Año inicio')
    institution = models.CharField(max_length=100, blank=True, verbose_name='Institución')
    INST_TYPE_CHOICES = (
        ('ayto', 'Ayuntamiento'),
        ('auto', 'Autónoma'),
        ('priv', 'Privado'),
        ('fora', 'Foral'),
    )
    institution_type = models.CharField(max_length=4, choices=INST_TYPE_CHOICES, blank=True, verbose_name='Tipo institución')
    open_times = models.CharField(max_length=255, null=True,blank=True, verbose_name='Horario apertura')
    ACCESS_TYPE_CHOICES = (
        ('l', 'Libre'),
        ('r', 'Restringido'),
    )
    access_type = models.CharField(max_length=1, choices=ACCESS_TYPE_CHOICES, blank=True, verbose_name='Tipo de acceso')
    CENTER_TYPE_CHOICES = (
        ('p', 'Público'),
    )
    center_type = models.CharField(max_length=1, choices=CENTER_TYPE_CHOICES, blank=True, verbose_name='Tipo de centro')
    topics = models.ManyToManyField(Bibtopic, verbose_name='Temas')
    services = models.ManyToManyField(Bibservice, verbose_name='Servicios')   
    place=models.ForeignKey(Place, unique=True, verbose_name='Place', related_name='biblio')

class MPhoto(ImageModel):
    name=models.CharField(max_length=255, verbose_name='Nombre', blank=True)
    place=models.ForeignKey(Place, verbose_name='Place')
    user=models.ForeignKey(User, verbose_name='User', blank=True, null=True)
    def_img = models.BooleanField(verbose_name='Default',default=False)    
    
    def __unicode__(self):
        return self.name or self.place.name
    

def generate_place_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_proposal = slugify(u'%s' % (instance.name))
        prev_slug = Place.objects.filter(slug__startswith=slug_proposal).exclude(pk=instance.pk)
        if prev_slug:
            slug_proposal += u'-%s' % len(prev_slug)
        instance.slug = slug_proposal
pre_save.connect(generate_place_slug, sender=Place)

	
def send_image_notification(sender, instance, created, **kwargs):
    if created:
        send_mail('[IRUDI BERRIA] ', 'Irudi berri bat gorde da: '+instance.name+'\n\n'+settings.HOST+'/admin/places/mphoto/' + str(instance.id), DEFAULT_FROM_EMAIL,
            [EMAIL_NOTIFICATION], fail_silently=True)	
    return True

post_save.connect(send_image_notification, sender=MPhoto)
