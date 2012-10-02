from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, Access, Biblio, Bibtopic, Bibservice
from arartekomaps.locations.models import Location
from arartekomaps.locations.utils import slugify

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
             
    BDICT = {'Publikoa':'p',
             'Infantil':'i',
             'Pribatua':'r'}
             
    IDICT = {'Ayuntamiento':'ayto',
             'Erakunde autonoma':'auto',
             'Erakunde autonomaa':'auto',
             'Erakunde autonomoa':'auto',
             'Pribatua':'priv',
    
    }

    ACDICT = {'Libre':'l'
    }
    
    CDICT = {'Publico':'p'
    
    } 
    
    
    def handle(self, *args, **options):
        f = open(args[0],'r')
        parent = Location.objects.get(slug='gipuzkoa')
        #fix this, location's parent must be described in data file
        kont = 1
	for pl in f.readlines()[2:]:
            (titulo, slug, ent_origen, cod_origen, cat, 
            direc1, direc2, cp, pob, desc, tel, fax, url, 
            email, foto, lat, lon, foto_x, foto_x_tit, foto_x_alt, 
            acc_fis, acc_vis, acc_aud, acc_int, acc_org, tipo_biblio, 
            ano_inicio, institution, institution_type, open_times, 
            access_type, center_type, tem_general, tem_infantil, 
            tem_religioso, ser_consulta, ser_reprografia, ser_hemeroteca, 
            ser_wifi, ser_selectiva, ser_bol_novedades, ser_prestamo, 
            ser_prestamo_inter, ser_prestamo_domic, ser_infor_bibliografica, 
            ser_internet_usuarios, ser_acceso_bbdd) = pl.split('\t')[0:47]

            cat = 'biblioteka'
            cat_obj = Category.objects.get(slug=cat)                     
            cod_origen = "bib%04d" % (kont)
            
            
            location_slug = slugify(pob)           
            location = Location.objects.filter(slug__startswith=location_slug)
            if location:
                loc_obj = location[0]
            else:
                print 'ERROREA', location_slug
                break
                     
            place = Place()
            place.slug = slugify("%s_%s" % ('bib',pob), instance=place)
            
            print kont, titulo, place.slug, loc_obj.name, institution, self.IDICT[institution_type]
            place.name = titulo.decode('utf-8')
            place.category = cat_obj
            place.description = desc.decode('utf-8')
            place.address1 = direc1
            place.address2 = direc2
            if len(cp)<5:
                cp = "0%s" % cp
            place.postalcode = cp
            place.city = loc_obj
            place.description = desc
            place.source = ent_origen
            place.source_id = cod_origen
            if lat:
                place.lat = lat
            if lon:
                place.lon = lon
            place.tlf = tel
            place.fax = fax
            place.url = url
            place.email = email
            place.save()
            
            access = Access()
            access.aphysic = self.ADICT[acc_fis.lower().strip()]
            access.avisual = self.ADICT[acc_vis.lower().strip()]
            access.aaudio = self.ADICT[acc_aud.lower().strip()]
            access.aintelec = self.ADICT[acc_int.lower().strip()]
            access.aorganic = self.ADICT[acc_org.lower().strip()]
            access.place = place
            access.save()
             
            biblio = Biblio()
            biblio.btype = self.BDICT[tipo_biblio.strip()]
            ano_conv = ano_inicio.strip().replace('.','')
            try:
                biblio.start_year = int(ano_conv)
            except:
                biblio.start_year = 0
            biblio.institution = institution_type
            biblio.institution_type = self.IDICT[institution_type.strip()]
            biblio.open_times = open_times
            biblio.access_type = self.ACDICT[access_type.strip()]
            biblio.center_type = self.CDICT[center_type.strip()]
            biblio.place = place
            biblio.save()
            
            bibtopics = {'general':tem_general, 'infantil':tem_infantil, 'religioso':tem_religioso}             
            for k,v in bibtopics.items():
                if v:
                    bibtopic = Bibtopic.objects.filter(name=k)
                    if bibtopic:
                        bibtopic_obj = bibtopic[0]
                    else:
                        print 'ERROR: no bibtopic called %s' % k
                        bibtopic_obj = Bibtopic()
                        bibtopic_obj.name = k
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
                        bibservice_obj.save()
                    biblio.services.add(bibservice_obj)                                  


            biblio.save()
            kont += 1

