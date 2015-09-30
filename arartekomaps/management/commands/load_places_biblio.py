from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category

from arartekomaps.arartekouser.models import ArartekoUser as User

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
             'sin datos': 's',
             'sin_datos': 's',
             '':'s',
             'practicable': 'p',
             'accesible': 'a',
             'accesble':'a'
             }

    BDICT = {'Publikoa':'p',
             'Infantil':'i',
             'Pribatua':'r',
             '':'X'}

    IDICT = {'Ayuntamiento':'ayto',
             'Erakunde autonoma':'auto',
             'Erakunde autonomaa':'auto',
             'Erakunde autonomoa':'auto',
             'Pribatua':'priv',
             '':'XXXX',

    }

    ACDICT = {'Libre':'l',
             '':'X',
    }

    CDICT = {'Publico':'p',
             '':'X'

    }

    BSDICT = {'EGIAZKOA':1,
              1:1,
              'FALTSUA':0,
              '0':0,
              0:0,

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

        cat = 'library'
        cat_obj = Category.objects.get(slug=cat)

        for rownum in range(sh.nrows)[1:]:
            fields = sh.row_values(rownum)

            if len(fields)!=51:
                print 'Tenemos mas o menos de 51 campos'
                n = 1
                for field in fields:
                    print n, field
                    n = n+1
                break
            else:
                (cod_origen, titulo, slug, ent_origen, cod_origen_vacio, cat,
                direc1, direc2, cp, pob, city, desc, tel, fax, url,
                email, foto, lat, lon, foto_x, foto_x_tit, foto_x_alt,
                acc_fis, acc_vis, acc_aud, acc_int, acc_org, tipo_biblio,
                ano_inicio, instit, tipo_inst, open_times_eu,
                open_times_es, open_times_s_eu, open_times_s_es,
                tipo_acceso, tipo_centro, tematica_general,
                ser_consulta,
                ser_reprografia, ser_hemeroteca,
                ser_wifi, ser_selectiva, ser_bol_novedades, ser_prestamo,
                ser_prestamo_inter, ser_prestamo_domic, ser_infor_bibliografica,
                ser_internet_usuarios, ser_acceso_bbdd, latlon) = fields[:51]

            # Set fields because not used anymore
            loc = ''
            tipo_biblio = ''
            access_type = ''
            center_type = ''
            tem_general = ''
            institution = ''
            institution_type = ''


            cod_origen = "%d" % cod_origen
            ent_origen = 'ejgv_biblio'
            author = User.objects.get(username=ent_origen)

            location_slug = slugify(city or pob)
            location = Location.objects.filter(slug__startswith=location_slug)
            if location:
                loc_obj = location[0]
            else:
                print 'ERROREA', location_slug
                break

            places = Place.objects.filter(source_id=cod_origen, source=ent_origen)

            if len(places)>0:
                place = places[0]
                print 'EDIT:', place.slug, place.source, place.source_id
            else:
                place = Place()
                place.slug = slugify(titulo, instance=place)
                print 'NEW:', slug, cod_origen

            place.name = titulo
            place.category = cat_obj
            place.description_es = desc
            place.description_eu = desc
            place.description_en = desc
            place.address1 = direc1
            place.address2 = direc2
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp.strip()
            place.city = loc_obj
            place.locality = loc
            place.source = ent_origen
            place.source_id = cod_origen
            place.author = author
            try:
                (lat,lon) = latlon.split(',')
            except:
                print 'LATLONERROR', place.slug, latlon
                pass

            if lat:
                place.lat = lat
            if lon:
                place.lon = lon
            print place.lat, place.lon
            place.tlf = tel
            place.fax = fax
            place.url = url
            place.email = email
            place.modified_date = now

            # ACCESS
            place.aphysic = self.ADICT[acc_fis.lower().strip()]
            place.avisual = self.ADICT[acc_vis.lower().strip()]
            place.aaudio = self.ADICT[acc_aud.lower().strip()]
            place.aintelec = self.ADICT[acc_int.lower().strip()]
            place.aorganic = self.ADICT[acc_org.lower().strip()]

            #get photo URL:
            if foto:
                startx = foto.find('img src=')
                endx = foto.find('"', startx+10)
                foto_x = foto[startx+9:endx]

            if saving:
                place.save()

            #Load foto_x
            print foto_x
            t_place = place
            has_point = foto_x.split('/')[-1].find('.')
            if not foto_x_tit:
                foto_x_tit = place.name[:]
            if has_point>-1:
                if saving:
                    image = loadUrlImage(foto_x, t_place, foto_x_tit, 'jpg', )


            

            #BIBLIO
            try:
                biblio = place.biblio.all()[0]
            except:
                biblio = Biblio()
                biblio.place = place

            biblio.btype = self.BDICT[tipo_biblio.strip()]
            if ano_inicio:
                ano_conv = str(int(ano_inicio)).strip().replace('.','')
            else:
                ano_conv = ''
            try:
                biblio.start_year = int(ano_conv)
            except:
                biblio.start_year = 0
            biblio.institution = institution_type
            biblio.institution_type = self.IDICT[institution_type.strip()]
            open_times = "%s %s" % (open_times_eu, open_times_es)
            biblio.open_times = open_times[:250]
            biblio.access_type = self.ACDICT[access_type.strip()]
            biblio.center_type = self.CDICT[center_type.strip()]

            if saving:
                biblio.save()

            tem_infantil = ''
            tem_religioso = ''
            bibtopics = {'general':'1', 'infantil':tem_infantil, 'religioso':tem_religioso}
            for k,v in bibtopics.items():
                if v:
                    bibtopic = Bibtopic.objects.filter(name=k)
                    if bibtopic:
                        bibtopic_obj = bibtopic[0]
                    else:
                        print 'ERROR: no bibtopic called %s' % k
                        bibtopic_obj = Bibtopic()
                        bibtopic_obj.name = k
                        if saving:
                            bibtopic_obj.save()
                    biblio.topics.add(bibtopic_obj)

            bibservices = {'consulta':ser_consulta, 'reprografia':ser_reprografia,
                           'hemeroteca':ser_hemeroteca, 'wifi':ser_wifi, 'selectiva':ser_selectiva,
                           'bol_novedades':ser_bol_novedades, 'prestamo':ser_prestamo,
                           'prestamo_inter':ser_prestamo_inter, 'prestamo_domic':ser_prestamo_domic,
                           'infor_bibliografica':ser_infor_bibliografica, 'internet_usuarios':ser_internet_usuarios,
                           'acceso_bbdd':ser_acceso_bbdd
                           }
            for k,v in bibservices.items():
                if v:
                    bibservice = Bibservice.objects.filter(name=k)
                    if bibservice:
                        bibservice_obj = bibservice[0]
                    else:
                        print 'ERROR: no bibservice called %s' % k
                        bibservice_obj = Bibservice()
                        bibservice_obj.name = k
                        if saving:
                            bibservice_obj.save()
                    biblio.services.add(bibservice_obj)

            if saving:
                biblio.save()
            kont += 1

