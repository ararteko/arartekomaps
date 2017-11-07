#* - encoding: utf-8 -*
from django.db import models
from utils import slugify
from django.db.models.signals import pre_save
from arartekomaps.locations.models import Location
from arartekomaps.categories.models import Category
from photologue.models import ImageModel
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    User = settings.AUTH_USER_MODEL
except ImportError:
    from django.contrib.auth.models import User
from django.db.models import Count
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
    slug=models.SlugField(max_length=255, blank=True, null=True, unique=True, help_text=_('Si esta vacio se actualiza al guardar'))
    name=models.CharField(max_length=255, verbose_name=_('Nombre'))
    category=models.ForeignKey(Category, verbose_name=_('Categoria'))
    description =models.TextField(null=True, blank=True, verbose_name=_('Description'), help_text=_('Descripcion del lugar'))
    address1=models.CharField(max_length=100, blank=True, verbose_name=_('Address 1'), help_text=_('Direccion 1 del lugar'))
    address2=models.CharField(max_length=100, blank=True, verbose_name=_('Address 2'), help_text=_('Direccion 2 del lugar'))
    postalcode=models.CharField(max_length=5, blank=True, verbose_name=_('Codigo postal'), help_text=_('Codigo postal del municipio'))
    city=models.ForeignKey(Location, verbose_name=_('Municipio'), help_text=_('Nombre del municipio'))
    locality=models.CharField(max_length=100, blank=True, verbose_name=_('Localidad'), help_text=_('Nombre de localidad'))
    source=models.CharField(max_length=20, blank=True, verbose_name=_('Codigo entidad'))
    source_id=models.CharField(max_length=20, blank=True, verbose_name=_('Codigo origen'), help_text=_('Codigo de la ficha en la base de datos de origen'))
    lat=models.DecimalField(max_digits=12, decimal_places=8,null=True,blank=True, verbose_name=_('Latitud'), help_text=_('Latitud GPS'))
    lon=models.DecimalField(max_digits=12, decimal_places=8,null=True,blank=True, verbose_name=_('Longitud'), help_text=_('Longitud GPS'))
    tlf=models.CharField(max_length=30, blank=True, verbose_name=_('Telefono'), help_text=_('Numero de telefono'))
    fax=models.CharField(max_length=15, blank=True, verbose_name=_('Fax'), help_text=_('Numero de FAX'))
    url_name = models.CharField(max_length=100, blank=True, verbose_name=_('Nombre URL'), help_text=_('Nombre descriptivo del URL'))
    url = models.CharField(max_length=255, blank=True, verbose_name=_('URL'), help_text=_('URL del sitio web'))
    email = models.CharField(max_length=255, blank=True, verbose_name=_('Email'), help_text=_('Email de contacto'))
    aphysic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Fisica'),default="s", help_text=_('Estado del acceso para minusvalia fisica'))
    avisual = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Visual'),default="s", help_text=_('Estado del acceso para minusvalia visual'))
    aaudio = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Audio'),default="s", help_text=_('Estado del acceso para minusvalia auditiva'))
    aintelec = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Intelectual'),default="s", help_text=_('Estado del acceso para minusvalia intelectual'))
    aorganic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Organica'),default="s", help_text=_('Estado del acceso para minusvalia organica'))
    adescription = models.TextField(null=True, blank=True, verbose_name=_('Description'), help_text=_('Descripcion de los datos de acceso'))
    afileurl = models.TextField(null=True, blank=True, verbose_name=_('URL ficha'), help_text=_('URL de la ficha'))

    # ALTER TABLE `places_place` ADD `author_id` INT(11) NOT NULL , ADD `added` DATETIME NOT NULL ;
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Autor'))
    added = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha creacion'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Fecha Modificacion'))

    # ALTER TABLE `places_place` ADD `is_public` BOOLEAN NOT NULL DEFAULT TRUE ;
    is_public = models.BooleanField(default=True, help_text=_('Mostrar publicamente este lugar'),verbose_name=_('Es publica'))

    def get_comments_count(self):
        return self.parent.all().count()

    def access_list(self):
        access_tuple = (
            ('aphysic', self.aphysic, _('aphysic'), _("access_%s" % self.aphysic)),
            ('avisual', self.avisual, _('avisual'), _("access_%s" % self.avisual)),
            ('aaudio', self.aaudio, _('aaudio'), _("access_%s" % self.aaudio)),
            ('aintelec', self.aintelec, _('aintelec'), _("access_%s" % self.aintelec)),
            ('aorganic', self.aorganic, _('aorganic'), _("access_%s" % self.aorganic))
            )
        return access_tuple

    def access_dict_list(self):
        acc = dict(ACCESS_CHOICES)
        access_dict = {
            'aphysic': acc[self.aphysic],
            'avisual': acc[self.avisual],
            'aaudio': acc[self.aaudio],
            'aintelec': acc[self.aintelec],
            'aorganic': acc[self.aorganic]
        }
        return access_dict

    def access_data(self):
        access_dict = {'description': self.adescription or '', 'fileurl': self.afileurl or '',
                        'aphysic': self.aphysic, 'avisual': self.avisual, 'aaudio': self.aaudio,
                        'aintelec': self.aintelec, 'aorganic': self.aorganic}
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
        AS distance FROM places_place WHERE (%f * acos( cos( radians(%f) ) * cos( radians( lat ) ) *
        cos( radians( lon ) - radians(%f) ) + sin( radians(%f) ) * sin( radians( lat ) ) ) ) < %d
        ORDER BY distance LIMIT 0 , %d;""" % (distance_unit, latitude, longitude, latitude ,distance_unit, latitude, longitude, latitude, int(radius), max_results)
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

    def save(self):
        if hasattr(self, 'custom_date'):
            self.modified_date = self.custom_date
        super(Place, self).save()



class Access(models.Model):
    aphysic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Fisica'))
    avisual = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Visual'))
    aaudio = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Audio'))
    aintelec = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Intelectual'))
    aorganic = models.CharField(max_length=1, choices=ACCESS_CHOICES, verbose_name=_('Organica'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    fileurl = models.TextField(null=True, blank=True, verbose_name=_('URL ficha'))
    place = models.ForeignKey(Place, unique=True, verbose_name=_('Place'), related_name='access')

class Bibtopic(models.Model):
    """ """
    name = models.CharField(max_length=50, verbose_name=_('Nombre'))

    def __unicode__(self):
        return self.name

class Bibservice(models.Model):
    """ """
    name = models.CharField(max_length=50, verbose_name=_('Nombre'))

    def __unicode__(self):
        return self.name

class Biblio(models.Model):
    BTYPE_CHOICES = (
        ('p', 'Publico'),
        ('r', 'Privado'),
        ('i', 'Infantil'),
        ('v', 'Investigacion'),
        ('t', 'Patrimonial'),
        ('e', 'Especializada')
    )
    btype = models.CharField(max_length=1, choices=BTYPE_CHOICES, null=True, blank=True, verbose_name=_('Tipo'))
    start_year = models.DecimalField(max_digits=4, decimal_places=0,null=True,blank=True, verbose_name=_('Ano inicio'))
    institution = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Institucion'))
    INST_TYPE_CHOICES = (
        ('ayto', 'Ayuntamiento'),
        ('auto', 'Autónoma'),
        ('priv', 'Privado'),
        ('fora', 'Foral'),
    )
    institution_type = models.CharField(max_length=4, choices=INST_TYPE_CHOICES, null=True, blank=True, verbose_name=_('Tipo institucion'))
    open_times = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Horario apertura'))
    ACCESS_TYPE_CHOICES = (
        ('l', 'Libre'),
        ('r', 'Restringido'),
    )
    access_type = models.CharField(max_length=1, choices=ACCESS_TYPE_CHOICES, null=True, blank=True, verbose_name=_('Tipo de acceso'))
    CENTER_TYPE_CHOICES = (
        ('p', 'Público'),
    )
    center_type = models.CharField(max_length=1, choices=CENTER_TYPE_CHOICES, null=True, blank=True, verbose_name=_('Tipo de centro'))
    topics = models.ManyToManyField(Bibtopic, verbose_name=_('Temas'))
    services = models.ManyToManyField(Bibservice, verbose_name=_('Servicios'))
    place=models.ForeignKey(Place, unique=True, verbose_name=_('Place'), related_name='biblio')

    def __unicode__(self):
        return u"%d" % (self.id)

class MPhoto(ImageModel):
    name=models.CharField(max_length=255, verbose_name=_('Nombre'), blank=True)
    place=models.ForeignKey(Place, verbose_name=_('Place'))
    user=models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True)
    def_img = models.BooleanField(verbose_name=_('Default img'),default=False)

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
    if created and not settings.DEBUG:
        send_mail('[IRUDI BERRIA] ', 'Irudi berri bat gorde da: '+instance.name+'\n\n'+settings.HOST+'/admin/places/mphoto/' + str(instance.id), DEFAULT_FROM_EMAIL,
            [EMAIL_NOTIFICATION], fail_silently=True)
    return True

def send_place_email(sender,instance, created, **kwargs):
    if created and not settings.DEBUG:
        send_mail('[LEKU BERRIA] ', 'Leku berri bat gorde da: '+instance.name+'\n\n'+settings.HOST+'/admin/places/place/' + str(instance.id), DEFAULT_FROM_EMAIL,
            [EMAIL_NOTIFICATION], fail_silently=True)

post_save.connect(send_image_notification, sender=MPhoto)
post_save.connect(send_place_email, sender=Place)
