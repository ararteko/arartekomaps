from django.core.management.base import BaseCommand
from arartekomaps.places.models import Place

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload place lat lon from file (CSV)'

    def handle(self, *args, **options):
        f = open(args[0],'r')
        cnt = 1
        for pl in f.readlines():
            print cnt
            (source_id,lat,lon)=pl.split('\t')[0:24]
            place = Place.objects.get(source_id=source_id) 
            print place.slug, place.lat, place.lon
            print lat,lon
            place.lat = lat
            place.lon = lon
            place.save()
