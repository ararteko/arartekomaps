from django.conf.urls.defaults import *
from piston.resource import Resource
from arartekomaps.api.handlers import LocationsHandler

location_handler = Resource(LocationsHandler)

urlpatterns = patterns('',
   url(r'^1.0/get_cities$', location_handler),
)