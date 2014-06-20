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

        cat = 'train'
        cat_obj = Category.objects.get(slug=cat)

        for rownum in range(sh.nrows)[1:]:
            fields = sh.row_values(rownum)

            if len(fields)!=24:
                print 'Tenemos mas o menos de 24 campos'
                n = 1
                for field in fields:
                    print n, field
                    n = n+1
                break
            else:
                (slug, name, cat_slug, description, address1, address2,
                 postalcode, city_name, locality, source, source_id, lat,
                 lon, tlf, fax, url, email,
                 acc_fis, acc_vis, acc_aud, acc_int, acc_org,
                 acc_desc, acc_fileurl) = fields[:24]
            
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
            location = Location.objects.filter(slug__startswith=location_slug)
            if location:
                loc_obj = location[0]
            else:
                print 'ERROREA', location_slug
                break
            print location_slug, location
            kont += 1

