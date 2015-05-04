from piston.handler import AnonymousBaseHandler, BaseHandler
from django.conf import settings
import json
import ast
from arartekomaps.locations.models import Location
from arartekomaps.categories.models import Category
from arartekomaps.places.models import Place, MPhoto
try:
    from django.contrib.auth import get_user_model
    User = settings.AUTH_USER_MODEL
except ImportError:
    from django.contrib.auth.models import User
from arartekomaps.mycomment.models import Comment
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, transaction
from smtplib import SMTPException
from registration.models import RegistrationProfile
from cssocialuser.models import CSSocialUser

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from arartekomaps.utils.load_images import handle_photo_file
from django.core.files.base import ContentFile

from social_auth.backends.pipeline.social import associate_user
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.models import UserSocialAuth
from social_auth.backends import get_backend
from django.utils import translation
import logging
import base64, urllib
from math import radians, cos, sin, asin, sqrt, degrees

logger = logging.getLogger(__name__)

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
        translation.activate(lang)
        try:
            locations = Location.objects.filter(level=2).order_by('name')
            json_loc = []
            for loc in locations:
                h = {'name': loc.name, 'slug': loc.slug}
                json_loc.append(h)
            return {'lang': lang, 'action': 'get_cities', 'result': 'success', 'values': json_loc}
        except:
            logger.error("Couldn't get location information")
            return {'lang': lang, 'action': 'get_cities', 'result': 'failed', 'value': 'generic_error', 'msg': translation.ugettext('Ezin izan da kokapen informazioa eskuratu')}


class CategoriesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Category

    def read(self, request):
        lang = request.GET.get("lang","eu")
        translation.activate(lang)
        try:
            categories = Category.objects.filter(parent=None).order_by('name')
            json_loc = []
            name = ''
            for cat in categories:
                if lang == 'eu':
                    name = cat.name_eu
                else:
                    name = cat.name_es
                h = {
                    'name': name,
                    'slug': cat.slug,
                    'icon': cat.icon()+'.png',
                }
                json_loc.append(h)
            return {'lang': lang, 'action': 'get_categories', 'result': 'success', 'values': json_loc}
        except:
            logger.error("Couldn't get categories")
            return {'lang': lang, 'action': 'get_categories', 'result': 'failed', 'value': 'generic_error', 'msg': translation.ugettext('Ezin dira kategoriak eskuratu')}

class PlaceHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Place

    def read(self, request):
        slug = request.GET.get("slug","")
        lang = request.GET.get("lang","eu")
        translation.activate(lang)
        try:
            place = Place.objects.get(slug=slug)
            if MPhoto.objects.filter(place=place, def_img=True).exists():
                image = MPhoto.objects.filter(place=place, def_img=True)[0].get_place_API_url()
                #image = settings.HOST+image.get_place_API_url()
            else:
                image = None

            comments = Comment.objects.filter(parent=place)
            comment_list = []
            for comment in comments:
                if comment.photo:
                    c_img = settings.HOST+comment.photo.get_place_API_url()
                else:
                    c_img = ""
                if comment.author.get_profile().get_photo():
                    u_img = settings.HOST+comment.author.get_profile().get_photo().get_profile_API_url()
                else:
                    u_img = ""
                comment_list.append({
                    "name": comment.author.get_profile().get_fullname(),
                    "user_photo": u_img,
                    "public_date": comment.public_date.date(),
                    "text": comment.body,
                    "photo": c_img,
                })


            if place.tlf.find('-'):
                place.tlf = place.tlf.split('-')[0].strip()

            # if lang == 'eu':
            #     desc = place.description_eu
            # else:
            desc = u"%s\n\n%s\n\n%s" % (place.description_es, _('Accessibility'), place.access_data()['description'])

            if lang == 'eu':
                cat = place.category.name_eu
            else:
                cat = place.category.name_es

            json = {
                "name": place.name,
                "slug": place.slug,
                "category": {"name": cat, "slug": place.category.slug, "icon": place.category.icon()+'.png'},
                "description": desc,
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
                "photo": image,
                "comments": comment_list
            }
            return {'lang': lang, 'action': 'get_place', 'result': 'success', 'values': json}
        except Exception, e:
            logger.error("ERROR: "+str(e))
            return {'lang': lang, 'action': 'get_place', 'result': 'failed', 'value': 'generic_error','msg': translation.ugettext('Sisteman errore bat gertatu da "lekua" eskuratzean: ')+str(e)}


class PlacesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Place

    def read(self, request):
        location = request.GET.get("location","")
        category = request.GET.get("category","")
        lang = request.GET.get("lang","eu")
        translation.activate(lang)
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
                    return {'lang': lang, 'action': 'get_places', 'result': 'failed', 'value': 'location_not_geolocalized', 'msg': translation.ugettext('Lekua ez dago geo-kokatuta. Jarri kontaktuan guneko administratzaileekin.')}
                lon1 = float(loc.lon)
                lat1 = float(loc.lat)
            elif lat and lon:
                lat1 = float(lat)
                lon1 = float(lon)
            else:
                return {'lang': lang, 'action': 'get_places', 'result': 'failed', 'value': 'not_lat_lon', 'msg': translation.ugettext('Latitude eta longitudeak ezin izan dira eskuratu.')}

            maxLat,minLat,maxLon,minLon = get_gps_box(lat1,lon1)
            args['lat__range'] = (str(minLat),str(maxLat))
            args['lon__range'] = (str(maxLon),str(minLon))

            if category:
                cat = Category.objects.get(slug=category)
                categories = []
                for csl in cat.get_children():
                    categories.append(csl.slug)
                categories.append(cat.slug)
                args['category__slug__in'] = categories

            if aphysic in ACCESS_KEYS:
                if aphysic == "a":
                    args['access__aphysic'] = aphysic
                elif aphysic == "p":
                    args['access__aphysic__in'] = ACCESS_KEYS
            if avisual in ACCESS_KEYS:
                if avisual == "a":
                    args['access__avisual'] = avisual
                elif avisual == "p":
                    args['access__avisual__in'] = ACCESS_KEYS
            if aaudio in ACCESS_KEYS:
                if aaudio == "a":
                    args['access__aaudio'] = aaudio
                elif aaudio == "p":
                    args['access__aaudio__in'] = ACCESS_KEYS
            if aintelec in ACCESS_KEYS:
                if aintelec == "a":
                    args['access__aintelec'] = aintelec
                elif aintelec == "p":
                    args['access__aintelec__in'] = ACCESS_KEYS
            if aorganic in ACCESS_KEYS:
                if aorganic == "a":
                    args['access__aorganic'] = aphysic
                elif aorganic == "p":
                    args['access__aorganic__in'] = ACCESS_KEYS

            places = Place.objects.filter(**args)

            for place in places:
                # if lang == 'eu':
                #     desc = place.description_eu
                # else:


                desc = u"%s\n\n%s\n\n%s" % (place.description_es, _('Accessibility'), place.access_data()['description'])

                if lang == 'eu':
                    cat = place.category.name_eu
                else:
                    cat = place.category.name_es

                json = {
                    "name": place.name,
                    "slug": place.slug,
                    "category": {"name": cat, "slug": place.category.slug, "icon": place.category.icon()+'.png'},
                    "description": desc,
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
                return {'lang': lang, 'action': 'get_filtered_places', 'result': 'failed', 'value': 'empty', 'msg': translation.ugettext('Egin duzun bilaketarako ez dugu ezer aurkitu.')}
            return {'lang': lang, 'action': 'get_filtered_places', 'result': 'success', 'values': json_list[:10]}
        except Exception, e:
            logger.error("ERROR: "+str(e))
            return {'lang': lang, 'action': 'get_filtered_places', 'result': 'failed', 'value': 'generic_error', 'msg': translation.ugettext('Sisteman errore bat gertatu da "lekuak" eskuratzean: ')+str(e)}

class UserHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    model = User

    def create(self, request):

        username = request.POST.get("username","")
        email = request.POST.get("email","")
        passw = request.POST.get("pass","")
        origin = request.POST.get("origin","")
        lang = request.GET.get("lang","eu")
        translation.activate(lang)

        full_name = request.POST.get("full_name","")
        biography = request.POST.get("biography","")
        oauth_token_secret = request.POST.get("secret","")
        oauth_token = request.POST.get("token","")
        expires = request.POST.get("expires","")
        social_id = request.POST.get("id","")
        photo = request.POST.get("photo","")


        if origin == "":
            if not username:
                logger.error("ERROR: There is not enough data")
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'not_enough_data', 'msg': translation.ugettext('Datu gehiago behar ditugu. Erabiltzaile izena, eposta edo pasahitza falta zaigu.')}
            elif passw and email:
                try:
                    site = Site.objects.get(id=settings.SITE_ID)
                    if not re.match(r'[\w-]+', username):
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'invalid_form_values', 'msg': translation.ugettext('Erabiltzaile izenak hizki, zenbaki eta @/./+/-/_ karaktereak bakarrik izan ditzazke.')}
                    RegistrationProfile.objects.create_inactive_user(username, email, passw, site)
                    return {'action': 'login_or_register', 'result': 'success'}
                except IntegrityError, e:
                    logger.error("ERROR: "+str(e))
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'integrity_error', 'msg': translation.ugettext('Erabiltzaile izen hau lehendik ere existitzen da. Mesedez, erabili beste izen bat.')}
                except SMTPException, e:
                    logger.error("ERROR: "+str(e))
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'smtp_error', 'msg': translation.ugettext('Arazo bat egon da aktibazio eposta bidaltzean')}
                except Exception as e:
                    logger.error("ERROR: "+str(e))
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'unknown_error', 'msg': translation.ugettext('Erabiltzailea erregistratzean errore bat gertatu da')}
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
                        logger.error("ERROR: User is not active")
                        return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_not_active', 'msg': translation.ugettext('Erabiltzailea ez dago aktibatuta. Mesedez, begiratu zure epostara bidali dugun mezua eta jarraitu aktibazio pausoak.')}
                else:
                    # Return an 'invalid login' error message.
                    logger.error("ERROR: User is not authenticated")
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_is_not_authenticated', 'msg': translation.ugettext('Erabiltzailea edo pasahitz okerrak. Mesedez, saiatu berriro.')}
            else:
                logger.error("ERROR: Not enough data")
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'not_enough_data', 'msg': translation.ugettext('Datu gehiago behar ditugu. Erabiltzaile izena, eposta edo pasahitza falta zaigu.')}
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
                    logger.error("ERROR:"+str(e))
                    return {'action': 'login_or_register', 'result': 'failed', 'value': 'integrity_error', 'msg': translation.ugettext('Erabiltzaile izen hau lehendik ere existitzen da. Mesedez, erabili beste izen bat.')}

            access_token = ast.literal_eval(access_token)
            try:
                backend = get_backend(SOCIAL_ORIGIN[origin], request, request.path)
                user = backend.do_auth(access_token['access_token'])
            except Exception as e:
                logger.error("ERROR: "+str(e))
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'auth_error', 'msg': translation.ugettext('Sare sozialetako autentikazioak huts egin du: ')+str(e)}
            if user and user.is_active:
                login(request, user)
                token = default_token_generator.make_token(user)
                # Redirect to a success page.
                return {'action': 'login_or_register', 'result': 'success', 'value': token, 'username': user.username}
            else:
                # Return a 'disabled account' error message
                logger.error("ERROR: User is not active!")
                return {'action': 'login_or_register', 'result': 'failed', 'value': 'user_not_active', 'msg': translation.ugettext('Erabiltzailea ez dago aktibatuta. Mesedez, begiratu zure epostara bidali dugun mezua eta jarraitu aktibazio pausoak.')}
        else:
            logger.error("ERROR: Wrong origin!")
            return {'action': 'login_or_register', 'result': 'failed', 'value': 'wrong_origin', 'msg': translation.ugettext('Jatorri ezezaguneko erabiltzailea. Jarri administratzaileekin harremanetan.')}

class CommentHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Comment

    def create(self, request):
        username = request.POST.get("username","")
        origin = request.POST.get("origin","")
        social_id = request.POST.get("id","")
        token = request.POST.get("token","")
        text = request.POST.get("text","")
        slug = request.POST.get("slug","")
        lang = request.GET.get("lang","eu")
        translation.activate(lang)

        f = open('post_saiakerak.txt','w')
        try:
            if origin in tuple(SOCIAL_ORIGIN.keys()):
                if origin == "1":
                    profile = CSSocialUser.objects.get(facebook_id=username)
                    user = profile.user
                else:
                    profile = CSSocialUser.objects.get(twitter_id=username)
                    user = profile.user
            else:
                user = User.objects.get(username=username)
                f.write('[OK] Username: '+username+' | Text: '+text+' | Slug: '+slug+' | Token: '+token+'\n')
        except:
            logger.error("ERROR: Invalid username")
            f.write('[ERROR] Username: '+username+' | Text: '+text+' | Slug: '+slug+' | Token: '+token+'\n')
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_username', 'msg': translation.ugettext('Erabiltzaile hori ez da sisteman existitzen. Jarri administratzailearekin kontaktuan.')}

        f.close()
        if default_token_generator.check_token(user,token):
            try:
                place = Place.objects.get(slug=slug)

                if text:
                    comment = Comment()
                    comment.author = user
                    comment.is_public = True
                    comment.public_date = datetime.today()
                    comment.parent = place
                    comment.body = text
                    comment.ip_address = request.META.get("REMOTE_ADDR", None)
                    if 'photo' in request.FILES:
                        try:
                            photo = handle_photo_file(request.FILES['photo'], user.username)
                        except Exception, e:
                            return {'action': 'post_comment', 'result': 'failed', 'value': 'decoding_error', 'msg': translation.ugettext('Irudiaren formatua ez da egokia. JPG formatuan bidali mesedez.')+str(e)}
                        comment.photo = photo
                    comment.save()
                    return {'action': 'post_comment', 'result': 'success'}
                else:
                    return {'action': 'post_comment', 'result': 'failed', 'value': 'text_not_found', 'msg': translation.ugettext('Iruzkinak ez dauka testurik. Testua beharrezkoa da.')}

            except Exception as e:
                logger.error("ERROR: "+str(e))
                return {'action': 'post_comment', 'result': 'failed', 'value': 'place_error', 'msg': translation.ugettext('Iruzkina utzi nahi den "lekua" aurkitzean errorea: ')+str(e)}
        else:
            logger.error("ERROR: Invalid token")
            return {'action': 'post_comment', 'result': 'failed', 'value': 'invalid_token', 'msg': translation.ugettext('Erabiltzaile saioa iraungi da. Berriz sartu zure erabiltzaile eta pasahitzarekin.')}

class GetCommentHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Comment

    def read(self, request):
        slug = request.GET.get("slug","")
        lang = request.GET.get("lang","eu")
        translation.activate(lang)
        try:
            place = Place.objects.get(slug=slug)
            comments = Comment.objects.filter(parent=place)
            comment_list = []
            for comment in comments:
                if comment.photo:
                    c_img = settings.HOST+comment.photo.get_place_API_url()
                else:
                    c_img = ""
                if comment.author.get_profile().get_photo():
                    u_img = settings.HOST+comment.author.get_profile().get_photo().get_profile_API_url()
                else:
                    u_img = ""
                comment_list.append({
                    "name": comment.author.get_profile().get_fullname(),
                    "user_photo": u_img,
                    "public_date": comment.public_date.date(),
                    "text": comment.body,
                    "photo": c_img,
                })
            return {'lang': lang, 'action': 'get_comments', 'result': 'success', 'values': comment_list}
        except Exception, e:
            logger.error("ERROR:"+str(e))
            return {'lang': lang, 'action': 'get_comments', 'result': 'failed', 'value': 'comments_error', 'msg': translation.ugettext('Iruzkinak eskuratzean errore bat gertatu da: ')+str(e)}