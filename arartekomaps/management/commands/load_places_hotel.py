from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice, MPhoto
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify
import xlrd, StringIO, urllib2
from arartekomaps.utils.load_images import loadUrlImage
import os

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (CSV)'
    ADICT = {'inaccesible':'n',
             'no_accesible':'n',
             'sin datos': 's',
             'sin_datos': 's',
             '':'s',
             'practicable': 'p',
             'accesible': 'a'}
    
    def handle(self, *args, **options):
        print os.listdir('.')
        f = xlrd.open_workbook(args[0])
        sh = f.sheet_by_index(0)
        kont = 1
        ercnt =1
        
        CDICT = {'legutiano':'legutio',
                 'ribera-alta':'erriberagoitia', 
        }

        uloc = {}

        for rownum in range(sh.nrows)[1:]:
            fields = sh.row_values(rownum)

            if len(fields)!=26:
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
                
            cat = slugify(rcat)
            rel_cat = Category.objects.filter(slug=cat)
            if len(rel_cat)>0:
                cat_obj = Category.objects.get(slug=cat)
            else:
                parentcat = Category.objects.get(slug='sleep')
                cat_obj = Category(slug=cat,name=cat,parent=parentcat)
                cat_obj.save()
                                 
            ent_origen = 'ejgv-tur-aloj'
                   
            location_slug = slugify(pob)

            if CDICT.has_key(location_slug):
                location_slug = CDICT[location_slug]           
            location = Location.objects.filter(slug__startswith=location_slug)
            if location:
                loc_obj = location[0]
            else:
                print ercnt,'ERROREA TOKI EZEZAGUNA', titulo, cp, pob, kont
                uloc[pob]=uloc.get(pob,0)+1
                ercnt = ercnt+1
                break
     
            place = Place()
            place.slug = slugify(slug.split('/')[2])
            
            try:
                print kont, titulo, place.slug, loc_obj.name
            except:
                print place.slug
            print "##%s##" % tel, len(tel) 
            place.name = titulo
            place.category = cat_obj
            place.description = desc
            place.address1 = direc1
            place.address2 = direc2
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp
            try:
                place.city = loc_obj
            except:
                pass
            place.locality = loc
            place.description = desc
            place.source = ent_origen
            place.source_id = cod_origen
            if lat:
                place.lat = lat
            if lon:
                place.lon = lon
            place.tlf = tel[:30]
            place.fax = fax[:15]
            place.url = url
            place.email = ''
            #place.save()
            
            access = Access()
            access.aphysic = self.ADICT[acc_fis.lower().strip()]
            access.avisual = self.ADICT[acc_vis.lower().strip()]
            access.aaudio = self.ADICT[acc_aud.lower().strip()]
            access.aintelec = self.ADICT[acc_int.lower().strip()]
            access.aorganic = self.ADICT[acc_org.lower().strip()]
            access.place = place
            #access.save()

                        
                        
            foto_x = foto_x.replace('http://turismo.euskadi.net/contenidos/a_alojamiento/ ','http://turismo.euskadi.net/x65-12375/es/contenidos/a_alojamiento/')
            print foto_x
            t_place = place #Place.objects.get(slug='bib-ikaztegieta')
            has_point = foto_x.split('/')[-1].find('.')
            if has_point>-1:
                image = loadUrlImage(foto_x, t_place, foto_x_tit, 'jpg', )            
            kont += 1

        print uloc
        
