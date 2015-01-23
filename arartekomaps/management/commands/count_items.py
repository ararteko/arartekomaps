from django.core.management.base import BaseCommand
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place

class Command(BaseCommand):
    args = 'file_abs_path'
    help = 'Upload places from file (CSV)'

    def handle(self, *args, **options):
        cats = Category.objects.all()
        for cat in cats:
            places = Place.objects.filter(category=cat)
            print cat.name, len(places)        
