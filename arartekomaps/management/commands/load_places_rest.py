# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice, MPhoto
from arartekomaps.arartekouser.models import ArartekoUser as User
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify
import xlrd, StringIO, urllib2
from arartekomaps.utils.load_images import loadUrlImage
from arartekomaps.settings import IMPORT_FILES_FOLDER

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
        line = len(args)>2 and int(args[2]) or 1
        filename = args[0]
        full_path = "%s/%s" % (IMPORT_FILES_FOLDER,filename)
        f = xlrd.open_workbook(full_path)
        sh = f.sheet_by_index(0)
        kont = 1
        ercnt =1
        
        CDICT = {'legutiano':'legutio',
                 'ribera-alta':'erriberagoitia', 
        }

        uloc = {}

        new_rest = 0

        for rownum in range(sh.nrows)[line:]:
            fields = sh.row_values(rownum)
            print '############################'
            print kont
            if len(fields)!=25:
                print 'Tenemos mas o menos de 25 campos'
                n = 1
                for field in fields:
                    print n, field
                    n = n+1
                break
            else:
                (titulo, slug, ent_origen, cod_origen, rcat, 
                direc1, direc2, cp, pob, loc, desc, lat, lon, tel, fax, url, 
                foto_x, foto_x_tit, foto_x_alt, itinerarios, 
                acc_fis, acc_vis, acc_aud, acc_int, 
                acc_org ) = fields[:25]


            translation = False
            ent_origen = 'ejgv-tur-rest'
            places = Place.objects.filter(source_id=cod_origen, source=ent_origen)
            if len(places)<1:
                places = Place.objects.filter(source_id=str(int(cod_origen)), source=ent_origen)
            if len(places)>0:
                place = places[0]
            if '_eu' in filename and place:
                place.description_eu = desc
                translation = True
            elif '_en' in filename and place:
                place.description_en = desc
                translation = True
            elif '_eu' in filename or '_en' in filename:
                translation = True

            if translation:
                place.save()
                continue
                
            #GET USER!!!!
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
                print 'EDIT:', slug, cod_origen
            else:
                place = Place()
                print slug
                place.slug = slugify(slug.split('/')[2],instance=place)
                print 'NEW:', slug, cod_origen

                if rcat: 
                    cat = slugify(rcat)
                    cat = self.RDICT.get(cat,cat)
                    rel_cat = Category.objects.filter(slug=cat)
                    if len(rel_cat)>0:
                        cat_obj = Category.objects.get(slug=cat)
                    else:
                        print 'WARNING: Missing cat:', cat
                        parentcat = Category.objects.get(slug='sleep')
                        cat_obj = Category(slug=cat,name=cat,name_es=cat,name_eu=cat,name_en=cat,parent=parentcat)
                        if saving:
                            cat_obj.save()
                else:
                    cat_obj = Category.objects.get(slug='sleep')

                place.category = cat_obj

                new_rest +=1
            
            place.name = titulo
            place.description_es = desc
            place.address1 = direc1
            place.address2 = ""
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp.strip()
            try:
                place.city = loc_obj
            except:
                pass
            place.locality = pob != loc and loc or ""
            place.description = desc
            place.source = ent_origen
            place.source_id = "%d" % int(cod_origen)
            if lat:
                place.lat = str(lat)
            if lon:
                place.lon = str(lon)

            #SET USER!!!!!
            place.author = author
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

        print "New restaurants: %d" % (new_rest)
        print uloc
        
