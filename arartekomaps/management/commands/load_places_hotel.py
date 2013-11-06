from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice, MPhoto
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify
import xlrd, StringIO, urllib2
from arartekomaps.utils.load_images import loadUrlImage
from arartekomaps.settings import IMPORT_FILES_FOLDER

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (XLS)'
    ADICT = {'inaccesible':'n',
             'no_accesible':'n',
             'sin datos': 's',
             'sin_datos': 's',
             '':'s',
             'practicable': 'p',
             'accesible': 'a'}
    
    def handle(self, *args, **options):
        saving = 1
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

        for rownum in range(sh.nrows)[1:]:
            fields = sh.row_values(rownum)

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
                
            cat = slugify(rcat)
            rel_cat = Category.objects.filter(slug=cat)
            if len(rel_cat)>0:
                cat_obj = Category.objects.get(slug=cat)
            else:
                print 'WARNING: Missing cat:', rcat
                parentcat = Category.objects.get(slug='sleep')
                cat_obj = Category(slug=cat,name=cat,parent=parentcat)
                if saving:
                    cat_obj.save()
                                 
            ent_origen = 'ejgv-tur-aloj'
                   
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
     
            places = Place.objects.filter(source_id=cod_origen, source=ent_origen)
            if len(places)<1:
                places = Place.objects.filter(source_id=str(int(cod_origen)), source=ent_origen)

            if len(places)>0:
                place = places[0]
                print 'EDIT:', slug, cod_origen
            else:
                place = Place()
                place.slug = slugify(slug.split('/')[2])
                print 'NEW:', slug, cod_origen
            

            place.name = titulo
            place.category = cat_obj
            place.description_eu = desc
            place.description_es = desc
            place.description_en = desc
            place.address1 = direc1
            place.address2 = direc2
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp.strip()
            try:
                place.city = loc_obj
            except:
                pass
            place.locality = loc
            place.description = desc
            place.source = ent_origen
            place.source_id = "%d" % int(cod_origen)
            if lat:
                place.lat = str(lat)
            if lon:
                place.lon = str(lon)
            place.tlf = ''.join(tel[:30].split())
            place.fax = ''.join(fax[:15].split())
            place.url = url
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

                        
                        
            foto_x = foto_x.replace('http://turismo.euskadi.net/contenidos/a_alojamiento/ ','http://turismo.euskadi.net/x65-12375/es/contenidos/a_alojamiento/')
            #print foto_x
            t_place = place
            has_point = foto_x.split('/')[-1].find('.')
            if has_point>-1:
                if saving:
                    image = loadUrlImage(foto_x, t_place, foto_x_tit, 'jpg', )            
            kont += 1

        print uloc
        
