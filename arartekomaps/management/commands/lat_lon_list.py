from django.core.management.base import BaseCommand
from arartekomaps.places.models import Place


class Command(BaseCommand):
    args = ''
    help = 'Download CSV with latlon'   
    
    def handle(self, *args, **options):
        places = Place.objects.filter(source='ejgv_biblio')
        for place in places:
            print "%s\t%s\t%s" % (place.source_id, place.lat, place.lon)