from piston.handler import AnonymousBaseHandler, BaseHandler
from django.conf import settings
import json
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place, MPhoto
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, transaction
from smtplib import SMTPException
from registration.models import RegistrationProfile

import base64, urllib
from math import radians, cos, sin, asin, sqrt, degrees

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
    km = 6371 * c
    return km

def get_gps_box(lat, lon):
    R = 6371
    radius = 50 
    maxLon = lon - degrees(float(radius)/R/cos(radians(lat)))
    minLon = lon + degrees(float(radius)/R/cos(radians(lat)))
    maxLat = lat + degrees(float(radius)/R)
    minLat = lat - degrees(float(radius)/R)
    return maxLat, minLat, maxLon, minLon


class LocationsHandler(AnonymousBaseHandler):
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

class PlaceHandler(AnonymousBaseHandler):
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
  

class PlacesHandler(AnonymousBaseHandler):
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
            else:
                lat1 = float(request.GET.get("lat",""))
                lon1 = float(request.GET.get("lon",""))
                maxLat,minLat,maxLon,minLon = get_gps_box(lat1,lon1)
                args['lat__range'] = (minLat,maxLat)
                args['lon__range'] = (maxLon,minLon)

            if category:
                args['category__slug'] = category

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
                    "comment_count": 0, 
                }
                json_list.append(json)
            json_list = sorted(json_list, key=lambda k: k['distance'])
            if not json_list:
                return {'lang': lang, 'action': 'get_places', 'result': 'failed'}
            return {'lang': lang, 'action': 'get_places', 'result': 'success', 'values': json_list}
        except:
            return {'lang': lang, 'action': 'get_places', 'result': 'failed'}


class UserHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    model = User

    def create(self, request):
        username = request.POST.get("username","")
        email = request.POST.get("email","")
        passw = request.POST.get("pass","")
        origin = request.POST.get("origin","")

        if origin:
            if origin == "0": 
                if not username:
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'not_enough_data'}
                elif passw and email:
                    try:
                        with transaction.atomic():
                            site = Site.objects.get(id=settings.SITE_ID)
                            print "hemen"
                            RegistrationProfile.objects.create_inactive_user(username, email, passw, site)
                            return {'action': 'login_or_register', 'result': 'success'}
                    except IntegrityError:
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'integrity_error'}
                    except SMTPException, e:
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'smtp_error: '+str(e)}
                    except Exception as e:
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'unknown_error: '+str(e)}
                elif passw and not email:
                    user = authenticate(username=username, password=passw)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            token = default_token_generator.make_token(user)
                            # Redirect to a success page.
                            return {'action': 'login_or_register', 'result': 'success', 'value': token}
                        else:
                            # Return a 'disabled account' error message
                            return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_not_active'}
                    else:
                        # Return an 'invalid login' error message.
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_is_not_authenticated'}
                else:
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'not_enough_data'}
        else:
            return {'action': 'login_or_register', 'result': 'failed', 'value': 'origin_not_found'}

class CommentHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Comment

    def create(self, request):
        username = request.POST.get("username","")
        token = request.POST.get("token","")
        text = request.POST.get("text","")

        try:
            user = User.objects.get(username=username)
        except:
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_username'}
        if default_token_generator.check_token(user,token):
            if text:
                return {'action': 'post_comment', 'result': 'success'}
            else:
                return {'action': 'post_comment', 'result': 'failed', 'value': 'text_not_found'}
        else:
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_token'}