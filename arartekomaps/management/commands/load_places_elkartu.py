from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice

from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify
from datetime import datetime

import xlrd

from arartekomaps.utils.load_images import loadUrlImage
from arartekomaps.settings import IMPORT_FILES_FOLDER

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (CSV)'
    ADICT = {'inaccesible':'n',
             'no_accesible':'n',
             'no_accesilbe':'n',
             'no_acesible':'n',
             'no_accedible':'n',
             'no accesible':'n',
             'sin datos': 's',
             'sin_datos': 's',
             '':'s',
             'practicable': 'p',
             'accesible': 'a',
             'accesble':'a'
             }
    CATDICT = {
            'Bares':'bar',
            'Restaurante':'restaurant',
            u'Pasteler\xeda':'pasteleria',
            'Otros':'eat',
            u'Comida r\xe1pida':'fast-food',
            u'Comida R\xe1pida':'fast-food',
            u'Sidrer\xeda':'sidreria',
            }

    def handle(self, *args, **options):
        saving = 1
        filename = args[0]
        full_path = "%s/%s" % (IMPORT_FILES_FOLDER,filename)
        f = xlrd.open_workbook(full_path)
        sh = f.sheet_by_index(0)

        kont = 1
        now = datetime.now()
        print 'NOW!:'
        print now


        for rownum in range(sh.nrows)[2:]:
            fields = sh.row_values(rownum)

            if len(fields)!=19:
                print 'Tenemos mas o menos de 19 campos'
                n = 1
                for field in fields:
                    print n, field
                    n = n+1
                break
            else:
                (name, catname, address1, postalcode,
                city_name, province, lat,
                 lon, tlf,
                 acc_fis, acc_vis, acc_aud, acc_int, acc_org,
                 acc_desc, xw, xx, xy, xz) = fields[:19]

            """slug
                name
                category.slug
                description
                address1
                address2
                postalcode
                city.name
                locality
                source
                source_id
                lat
                lon
                tlf
                fax
                url
                email
                access.aphysic
                access.avisual
                access.aaudio
                access.aintelec
                access.aorganic
                access.description
                access.fileurl
            """

            location_slug = slugify(city_name)
            try:
                location = Location.objects.get(slug=location_slug)
                loc_obj = location
            except:
                location = Location.objects.filter(slug__startswith=location_slug)
                if location:
                    loc_obj = location[0]
                else:
                    print 'ERROREA', location_slug
                    break
            print location, city_name, location_slug

            # Line added to force slug creation for the first import
            slug = "abcdefghijklmnopqrs"
            source_id = "%04d" % rownum
            source = 'elkartu'


            cat = self.CATDICT[catname]
            cat_obj = Category.objects.get(slug=cat)


            places = Place.objects.filter(slug=slug)

            if len(places)>0:
                place = places[0]
                print 'EDIT:', place.slug, place.source, place.source_id
            else:
                place = Place()
                place.slug = slugify(name, instance=place)
                print 'NEW:', place.slug, source_id
            place.name = name.encode('utf-8')
            place.category = cat_obj
            place.description_es = ''
            place.description_eu = ''
            place.description_en = ''
            place.address1 = address1
            place.address2 = ''
            cp = str(int(postalcode))
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp.strip()
            place.city = loc_obj
            place.locality = ''
            place.source = source
            place.source_id = source_id
            latstr = str(lat)[:-2]
            if type(lon)==type(0.3):
                lonstr =str(lon)[:-2]
            else:
                lonstr = lon
            place.lat = "%s.%s" % (latstr[:2],latstr[2:])
            place.lon = "%s.%s" % (lonstr[:2],lonstr[2:])
            print place.lat
            print place.lon
            place.tlf = tlf
            place.fax = ''
            place.url = ''
            place.email = ''
            place.modified_date = now

            if saving:
                place.save()

            # ACCESS
            try:
                access = place.access.all()[0]
            except:
                access = Access()
                access.place = place

            access.aphysic = self.ADICT[acc_fis.lower().strip()]
            access.avisual = self.ADICT[acc_vis.lower().strip()]
            access.aaudio = self.ADICT[acc_aud.lower().strip()]
            access.aintelec = self.ADICT[acc_int.lower().strip()]
            access.aorganic = self.ADICT[acc_org.lower().strip()]
            access.description = acc_desc

            if saving:
                access.save()

            kont += 1

