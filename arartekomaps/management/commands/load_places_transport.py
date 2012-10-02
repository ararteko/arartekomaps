from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (CSV)'
    ADICT = {'inaccesible':'n',
             'sin datos': 's',
             'practicable': 'p',
             'accesible': 'a'}

    def handle(self, *args, **options):
        f = open(args[0],'r')
        parent = Location.objects.get(slug='gipuzkoa')
        #fix this, location's parent must be described in data file
        kont = 1
        for pl in f.readlines()[1:]:
            print kont, len(pl.split('\t')), pl.split('\t')[0], pl.split('\t')[-2]
            (titulo, slug, ent_origen, cod_origen, 
            cat, direc, cp, pob, desc, tel, fax, url, 
            foto, lat, lon, foto_x, foto_x_tit, foto_x_alt, itinerarios,
            acc_fis, acc_vis, acc_aud, acc_int, 
            acc_org, imagen_titulo, imagen_alt, tipo_biblio,
            ano_inicio, institucion, tipo_institucion, codigo_portal,
            horarios, tipo_acceso, tipo_centro, tematica, servicios,
            snbe, snbe_url, bilgunea, bilgunea_url, bilgunea_fecha,
            acces_itinerario, acces_url_ficha ) = pl.split('\t')[:43]

            cat_obj = Category.objects.get(slug=cat)
            location_slug =slugify(pob)
            location = Location.objects.filter(slug__startswith=location_slug)

            if location:
                loc_obj = location[0]
            else:
                loc_obj = Location()
                loc_obj.name = pob.decode('utf-8')
                loc_obj.parent = parent
                loc_obj.save()
            place = Place()
            place.name = titulo.decode('utf-8')
            place.category = cat_obj
            place.description = desc.decode('utf-8')
            place.address1 = direc
            place.postalcode = cp
            place.city = loc_obj
            place.source = ent_origen
            place.source_id = cod_origen
            if lat:
                place.lat = lat
            if lon:
                place.lon = lon
            place.tlf = tel
            place.fax = fax
            place.url = url
            place.save()
            access = Access()
            access.aphysic = self.ADICT[acc_fis.lower().strip()]
            access.avisual = self.ADICT[acc_vis.lower().strip()]
            access.aaudio = self.ADICT[acc_aud.lower().strip()]
            access.aintelec = self.ADICT[acc_int.lower().strip()]
            access.aorganic = self.ADICT[acc_org.lower().strip()]
            access.description = acces_itinerario
            access.fileurl = acces_url_ficha
            access.place = place
            access.save()
            kont += 1

