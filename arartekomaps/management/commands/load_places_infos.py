# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice, MPhoto
from arartekomaps.arartekouser.models import ArartekoUser as User
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify
from django.utils.html import strip_tags
import xlrd, StringIO, urllib2
from arartekomaps.utils.load_images import loadUrlImage
from arartekomaps.settings import IMPORT_FILES_FOLDER
import re

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (CSV)'
    ADICT = {'inaccesible':'n',
             'no_accesible':'n',
             'no accesible':'n',
             'sin datos': 's',
             'sin_datos': 's',
             '':'s',
             'practicable': 'p',
             'accesible': 'a'}

    RDICT = {'restaurante':'restaurant',
            'sidreria':'sidreria',
            'asador':'asador',
            'bodega-de-vino-rioja-alavesa':'bodega-rioja',
            'bodega-de-txakoli':'bodega-txakoli',
            'comida-rapida':'fast-food',
            'pasteleria-confiteria':'pasteleria'
            }

    def handle(self, *args, **options):
        saving = len(args)>1 and args[1] or 0
        filename = args[0]
        line = len(args)>2 and int(args[2]) or 1
        full_path = "%s/%s" % (IMPORT_FILES_FOLDER,filename)
        f = xlrd.open_workbook(full_path)
        sh = f.sheet_by_index(0)
        kont = 1
        ercnt =1

        CDICT = {'legutiano':'legutio',
                 'ribera-alta':'erriberagoitia',
        }

        uloc = {}

        for rownum in range(sh.nrows)[line:]:
            fields = sh.row_values(rownum)

            if len(fields)!=25:
                print 'Tenemos mas o menos de 24 campos'
                n = 1
                for field in fields:
                    print n, field
                    n = n+1
                break
            else:
                (titulo, slug, ent_origen, cod_origen,
                direc1, direc2, cp, pob, loc, desc, lat, lon, tel, fax, url,
                foto_x, foto_x_tit, foto_x_alt, itinerarios,
                acc_fis, acc_vis, acc_aud, acc_int,
                acc_org, title_code ) = fields[:26]


            pattern = re.compile("\s+\d+")
            translation = False
            ent_origen = 'ejgv-tur-infos'
            places = Place.objects.filter(source_id=cod_origen, source=ent_origen)
            if len(places)<1:
                places = Place.objects.filter(source_id=str(int(cod_origen)), source=ent_origen)
            if len(places)>0:
                place = places[0]
            if '_eu' in filename and place:
                place.description_eu = strip_tags(desc)
                translation = True
            elif '_en' in filename and place:
                place.description_en = strip_tags(desc)
                translation = True
            elif '_eu' in filename or '_en' in filename:
                translation = True

            if translation:
                place.save()
                continue



            if 'oficinas' in filename:
                cat_obj = Category.objects.get(slug='tourist-office')
            elif 'centros' in filename:
                cat_obj = Category.objects.get(slug='interpretation-centre')
            else:
                cat_obj = Category.objects.get(slug='tourism')

            #GET USER
            author = User.objects.get(username=ent_origen)

            location_slug = slugify(pob)

            if CDICT.has_key(location_slug):
                location_slug = CDICT[location_slug]
            location = Location.objects.filter(slug__startswith=location_slug)
            if location:
                loc_obj = location[0]
            else:
                print ercnt,'WARNING: New place', titulo, cp, pob, kont
                uloc[pob]=uloc.get(pob,0)+1
                ercnt = ercnt+1
                break

            if len(places)>0:
                place = places[0]
                print 'EDIT:', place.slug, cod_origen
            else:
                place = Place()
                print slug
                place.slug = slugify(slug.split('/')[2],instance=place)
                print 'NEW:', slug, cod_origen


            if title_code:
                place.name = "%s %s" % (titulo, title_code)
            else:
                place.name = titulo
            place.category = cat_obj
            place.description_es = strip_tags(desc)
            repl = pattern.search(direc1)
            if "," not in direc1 and "km" not in direc1 and repl:
                repl = repl.group()
                direc1 = direc1.replace(repl, ",%s" % repl).replace("  ", " ").replace(" ,", ",")
            place.address1 = direc1.replace(u" Nº", "")
            place.address2 = direc2
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp.strip()
            try:
                place.city = loc_obj
            except:
                pass
            place.locality = pob != loc and loc or ""
            place.description = strip_tags(desc)

            #SET USER
            place.author = author
            place.source = ent_origen
            place.source_id = "%d" % int(cod_origen)
            if lat:
                place.lat = str(lat)
            if lon:
                place.lon = str(lon)
            place.tlf = ''.join(tel[:30].split())
            place.fax = ''.join(fax[:15].split())
            place.url = url
            place.url_es = url
            place.url_eu = url
            place.url_en = url
            place.email = ''
            if saving:
                place.save()

            accesses = Access.objects.filter(place=place)
            if len(accesses)>0:
                access = accesses[0]
            else:
                access = Access()
                access.place = place
            access.aphysic = self.ADICT[acc_fis.lower().strip()]
            access.avisual = self.ADICT[acc_vis.lower().strip()]
            access.aaudio = self.ADICT[acc_aud.lower().strip()]
            access.aintelec = self.ADICT[acc_int.lower().strip()]
            access.aorganic = self.ADICT[acc_org.lower().strip()]

            if saving:
                access.save()

            #print foto_x
            t_place = place
            has_point = foto_x.split('/')[-1].find('.')
            if has_point>-1:
                if saving:
                    image = loadUrlImage(foto_x, t_place, foto_x_tit, 'jpg', )
            kont += 1

        print uloc
