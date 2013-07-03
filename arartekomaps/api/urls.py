from django.conf.urls.defaults import *
from piston.resource import Resource
from arartekomaps.api.handlers import LocationsHandler, PlaceHandler, PlacesHandler, UserHandler, CommentHandler

location_handler = Resource(LocationsHandler)
place_handler = Resource(PlaceHandler)
places_handler = Resource(PlacesHandler)
user_handler = Resource(UserHandler)
comment_handler = Resource(CommentHandler)

urlpatterns = patterns('',
   url(r'^1.0/get_cities$', location_handler),
   url(r'^1.0/get_place$', place_handler),
   url(r'^1.0/get_places$', places_handler),
   url(r'^1.0/login_or_register$', user_handler),
   url(r'^1.0/post_comment$', comment_handler),
)