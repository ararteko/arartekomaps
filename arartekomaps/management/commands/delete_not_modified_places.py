from datetime import datetime
from django.core.management.base import BaseCommand
from arartekomaps.places.models import Place
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils.translation import activate

def delete_places(date, action=None, lang="es"):
    activate(lang)
    delete_places = Place.objects.filter(Q(author__username__startswith='ejgv'), Q(category__parent=11) | Q(category__parent=21) | Q(category__parent=22) | Q(category=11) | Q(category=21) | Q(category__parent=22), Q(modified_date__lt=date)).order_by('modified_date')

    for d in delete_places:
        print '"%s", "%s", "%s", "%s"' % (d.modified_date, d.name, _(d.category.name), d.author.username)
    print len(delete_places)

    if action:
        delete_places.delete()


class Command(BaseCommand):
    help = 'Delete not modified places'

    def handle(self, *args, **options):
        action = len(args) > 1 and arg[1] == 'True' and True or None
        lang = len(args) > 2 and args[2] or "es"
        date = len(args) > 0 or datetime.now()
        delete_places(action)