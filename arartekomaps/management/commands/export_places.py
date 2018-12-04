from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
import csv
import time
from django.template import loader, Context
from arartekomaps.places.models import Place
from django.conf import settings 

def export_places():
    places = Place.objects.all()

 #    with open('../media/places/places_'+str(time.strftime("%Y-%m-%d"))+'.csv', 'wb') as csvfile:
 #        str_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

 #        str_writer.writerow(["Name","Category","Address 1","Address 2","City","Postal Code","Locality","Telephone","Fax","URL","Email","Latitude","Longitude","Description"])
	# for place in places:
	#     str_writer.writerow([(place.name or '').encode('ascii', 'ignore'),(place.category.name or '').encode('ascii', 'ignore'),(place.address1 or '').encode('ascii', 'ignore'),(place.address2 or '').encode('ascii', 'ignore'),(place.city.name or '').encode('ascii', 'ignore'),(place.postalcode or '').encode('ascii', 'ignore'),(place.locality or '').encode('ascii', 'ignore'),(place.tlf or '').encode('ascii', 'ignore'),(place.fax or '').encode('ascii', 'ignore'),(place.url or '').encode('ascii', 'ignore'),(place.email or '').encode('ascii', 'ignore'),(str(place.lat) or ''),(str(place.lon) or ''),strip_tags((place.description or '')).encode('ascii', 'ignore')])

    t = loader.get_template('csv_export.txt')
    c = Context({
        'places': places,
    })
    with open("{}/places/place_{}.csv".format(settings.MEDIA_ROOT, str(time.strftime("%Y-%m-%d")), 'w') as myFile:
        myFile.write(t.render(c).encode('ascii', 'ignore'))
    return True

class Command(BaseCommand):
    help = 'Export places'

    def handle(self, *args, **options):
        export_places()