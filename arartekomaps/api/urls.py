from django.conf.urls.defaults import *
from piston.resource import Resource
from arartekomaps.api.handlers import LocationsHandler, PlaceHandler, PlacesHandler

location_handler = Resource(LocationsHandler)
place_handler = Resource(PlaceHandler)
places_handler = Resource(PlacesHandler)

urlpatterns = patterns('',
   url(r'^1.0/get_cities$', location_handler),
   url(r'^1.0/get_place$', place_handler),
   url(r'^1.0/get_places$', places_handler),
)