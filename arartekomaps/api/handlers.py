from piston.handler import BaseHandler
import json
from arartekomaps.locations.models import Location

class LocationsHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('name', 'slug')
    model = Location

    def read(self, request):
        locations = Location.objects.filter(level=2).order_by('name')
        json_loc = []
        for loc in locations:
            h = {'name': loc.name, 'slug': loc.slug}
            json_loc.append(h)
        #json_loc = json.dumps(json_loc)
        return {'lang': 'eu', 'action': 'get_cities', 'result': 'success', 'values': json_loc}
  