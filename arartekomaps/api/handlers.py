from piston.handler import AnonymousBaseHandler, BaseHandler
from django.conf import settings
import json
import ast
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place, MPhoto
from django.contrib.auth.models import User
from arartekomaps.mycomment.models import Comment
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, transaction
from smtplib import SMTPException
from registration.models import RegistrationProfile

from datetime import datetime
from arartekomaps.utils.load_images import handle_photo_file
from django.core.files.base import ContentFile

from social_auth.backends.pipeline.social import associate_user
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.models import UserSocialAuth
from social_auth.backends import get_backend
from django.utils.translation import ugettext_lazy as _

import base64, urllib
from math import radians, cos, sin, asin, sqrt, degrees

ACCESS_KEYS = ("a","p")

SOCIAL_ORIGIN = {"1": "facebook", "2": "twitter"}
SOCIAL_BACKEND = {"1": FacebookBackend, "2": TwitterBackend}

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
    R = float(6371)
    radius = float(5) 
    maxLon = lon - degrees(radius/R/cos(radians(lat)))
    minLon = lon + degrees(radius/R/cos(radians(lat)))
    maxLat = lat + degrees(radius/R)
    minLat = lat - degrees(radius/R)
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
            else:
                image_64 = ""

            comments = Comment.objects.filter(parent=place)
            comment_list = []
            for comment in comments:
                comment_list.append({
                    "name": comment.author.get_profile().get_fullname(),
                    "user_photo": "",
                    "public_date": comment.public_date.date(),
                    "text": comment.body,
                    "photo": "",
                })

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
                "comments": comment_list
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
        aphysic = request.GET.get("aphysic","")
        avisual = request.GET.get("avisual","")
        aaudio = request.GET.get("aaudio","")
        aintelec = request.GET.get("aintelec","")
        aorganic = request.GET.get("aorganic","")
        lat = request.GET.get("lat","")
        lon = request.GET.get("lon","")

        args = {}
        json_list = []
        try:
            if location:
                loc = Location.objects.get(slug=location)
                if not loc.lon or not loc.lat:
                    return {'lang': lang, 'action': 'get_places', 'result': 'failed', 'value': 'location_not_geolocalized'}
                lon1 = float(loc.lon)
                lat1 = float(loc.lat)
            elif lat and lon:
                lat1 = float(lat)
                lon1 = float(lon)
            else:
                return {'lang': lang, 'action': 'get_places', 'result': 'failed'}

            maxLat,minLat,maxLon,minLon = get_gps_box(lat1,lon1)
            args['lat__range'] = (str(minLat),str(maxLat))
            args['lon__range'] = (str(maxLon),str(minLon))

            if category:
                args['category__slug'] = category

            if aphysic in ACCESS_KEYS:
                if aphysic == "a":
                    args['access__aphysic'] = aphysic
                else:
                    args['access__aphysic__in'] = ACCESS_KEYS
            if avisual in ACCESS_KEYS:
                if avisual == "a":
                    args['access__avisual'] = avisual
                else:
                    args['access__avisual__in'] = ACCESS_KEYS
            if aaudio in ACCESS_KEYS:
                if aaudio == "a":
                    args['access__aaudio'] = aaudio
                else:
                    args['access__aaudio__in'] = ACCESS_KEYS
            if aintelec in ACCESS_KEYS:
                if aintelec == "a":
                    args['access__aintelec'] = aintelec
                else:
                    args['access__aintelec__in'] = ACCESS_KEYS
            if aorganic in ACCESS_KEYS:
                if aorganic == "a":
                    args['access__aorganic'] = aphysic
                else:
                    args['access__aorganic__in'] = ACCESS_KEYS

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
                    "comment_count": place.get_comments_count(), 
                }
                json_list.append(json)
            json_list = sorted(json_list, key=lambda k: k['distance'])
            if not json_list:
                return {'lang': lang, 'action': 'get_places', 'result': 'empty'}
            return {'lang': lang, 'action': 'get_places', 'result': 'success', 'values': json_list[:10]}
        except Exception, e:
            return {'lang': lang, 'action': 'get_places', 'result': 'failed', 'value': str(e)}


class UserHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    model = User

    def create(self, request):
        
        username = request.POST.get("username","")
        email = request.POST.get("email","")
        passw = request.POST.get("pass","")
        origin = request.POST.get("origin","")

        full_name = request.POST.get("full_name","")
        biography = request.POST.get("biography","")
        oauth_token_secret = request.POST.get("secret","")
        oauth_token = request.POST.get("token","")
        expires = request.POST.get("expires","")
        social_id = request.POST.get("id","")
        photo = request.POST.get("photo","")


        if origin == "": 
            if not username:
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'not_enough_data'}
            elif passw and email:
                try:
                    site = Site.objects.get(id=settings.SITE_ID)
                    RegistrationProfile.objects.create_inactive_user(username, email, passw, site)
                    return {'action': 'login_or_register', 'result': 'success'}
                except IntegrityError, e:
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'integrity_error: '+str(e)}
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
        elif origin in tuple(SOCIAL_ORIGIN.keys()):
            if origin == "1":
                access_token = u'{"access_token": "'+oauth_token+'", "expires": "'+expires+'", "id": '+social_id+'}'
            else:
                access_token = u'{"access_token": "oauth_token_secret='+oauth_token_secret+'&oauth_token='+oauth_token+'", "id": '+social_id+'}'
            if not User.objects.filter(username=username).exists():
                try:
                    user = User()
                    user.username = username
                    user.is_active = True
                    user.save()
                    usa, created = UserSocialAuth.objects.get_or_create(user=user, provider = SOCIAL_ORIGIN[origin], uid=int(social_id))
                    usa.extra_data = access_token
                    usa.save()
                except IntegrityError, e:
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'integrity_error: '+str(e)}

            access_token = ast.literal_eval(access_token)
            try:
                backend = get_backend(SOCIAL_ORIGIN[origin], request, request.path)
                user = backend.do_auth(access_token['access_token'])
            except Exception as e:
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'auth_error: '+str(e)}
            if user and user.is_active:
                login(request, user)
                token = default_token_generator.make_token(user)
                # Redirect to a success page.
                return {'action': 'login_or_register', 'result': 'success', 'value': token}
            else:
                # Return a 'disabled account' error message
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_not_active'}
        else:
            return {'action': 'login_or_register', 'result': 'failed', 'value': 'wrong_origin'}

class CommentHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Comment

    def create(self, request):
        username = request.POST.get("username","")
        token = request.POST.get("token","")
        text = request.POST.get("text","")
        slug = request.POST.get("slug","")

        try:
            user = User.objects.get(username=username)
        except:
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_username'}
        if default_token_generator.check_token(user,token):
            try:
                place = Place.objects.get(slug=slug)
            except Exception as e:
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'place_error: '+str(e)}
            if text:
                comment = Comment()
                comment.author = user
                comment.is_public = True
                comment.public_date = datetime.today()  
                comment.parent = place     
                comment.body = text
                comment.ip_address = request.META.get("REMOTE_ADDR", None)
                if photo:
                    try:
                        photo = handle_photo_file(request.FILES['photo'], user.username) 
                    except Exception, e:
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'decoding_error: '+str(e)}           
                    comment.photo = photo
                comment.save()
                return {'action': 'post_comment', 'result': 'success'}
            else:
                return {'action': 'post_comment', 'result': 'failed', 'value': 'text_not_found'}
        else:
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_token'}

