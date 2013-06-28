from piston.handler import BaseHandler
from django.conf import settings
import json
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place, MPhoto
import base64, urllib


from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    if km < 1:
        km = str(km * 1000)+"m"
    else:
        km = str(km)+"km"
    return km


class LocationsHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('name', 'slug')
    model = Location

    def read(self, request):
        lang = request.GET.get("lang","eu")
        try:
            locations = Location.objects.filter(level=2).order_by('name')
            json_loc = []
            for loc in locations:
                h = {'name': loc.name, 'slug': loc.slug}
                json_loc.append(h)
            return {'lang': lang, 'action': 'get_cities', 'result': 'success', 'values': json_loc}
        except:
            return {'lang': lang, 'action': 'get_cities', 'result': 'failed'}

class PlaceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Place

    def read(self, request):
        slug = request.GET.get("slug","")
        lang = request.GET.get("lang","eu")
        try:
            place = Place.objects.get(slug=slug)
            if MPhoto.objects.filter(place=place, def_img=True).exists():
                image = MPhoto.objects.filter(place=place, def_img=True)[0]
            image = urllib.urlopen(settings.HOST+image.image.url)
            image_64 = base64.encodestring(image.read())

            json = {
                "name": place.name,
                "slug": place.slug,
                "category": place.category.name,
                "description": place.description,
                "address1": place.address1,
                "address2": place.address2,
                "postalcode": place.postalcode,
                "city": place.city.name,
                "locality": place.locality,
                "source": place.source,
                "source_id": place.source_id,
                "lat": place.lat,
                "lon": place.lon,
                "tlf": place.tlf,
                "fax": place.fax,
                "url": place.url,
                "email": place.email,
                "accesibility": place.access_dict_list(),
                "photo": image_64,   
            }
            return {'lang': lang, 'action': 'get_place', 'result': 'success', 'value': json}
        except:
            return {'lang': lang, 'action': 'get_place', 'result': 'failed'}
  

class PlacesHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Place

    def read(self, request):
        location = request.GET.get("location","")
        category = request.GET.get("category","")
        lang = request.GET.get("lang","eu")
        args = {}
        json_list = []
        try:
            if location:
                args['city__slug'] = location
                loc = Location.objects.get(slug=location)
                lon1 = loc.lon
                lat1 = loc.lat
                if category:
                    args['category__slug'] = category
            
            print lon1,lat1
            places = Place.objects.filter(**args)
            for place in places:
                json = {
                    "name": place.name,
                    "slug": place.slug,
                    "category": place.category.name,
                    "description": place.description,
                    "address1": place.address1,
                    "address2": place.address2,
                    "postalcode": place.postalcode,
                    "city": place.city.name,
                    "locality": place.locality,
                    "lat": place.lat,
                    "lon": place.lon,
                    "distance": haversine(place.lon, place.lat, lon1, lat1),
                    "accesibility": place.access_dict_list(),  
                }
                json_list.append(json)
            return {'lang': lang, 'action': 'get_places', 'result': 'success', 'values': json_list}
        except:
            return {'lang': lang, 'action': 'get_places', 'result': 'failed'}