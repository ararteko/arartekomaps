from django.conf.urls.defaults import *
from piston.resource import Resource
from arartekomaps.api.handlers import *

location_handler = Resource(LocationsHandler)
category_handler = Resource(CategoriesHandler)
place_handler = Resource(PlaceHandler)
places_handler = Resource(PlacesHandler)
user_handler = Resource(UserHandler)
comment_handler = Resource(CommentHandler)
getcomment_handler = Resource(GetCommentHandler)

urlpatterns = patterns('',
   url(r'^1.0/get_cities$', location_handler),
   url(r'^1.0/get_categories$', category_handler),
   url(r'^1.0/get_place$', place_handler),
   url(r'^1.0/get_filtered_places$', places_handler),
   url(r'^1.0/get_comments$', getcomment_handler),
   url(r'^1.0/login_or_register$', user_handler),
   url(r'^1.0/post_comment$', comment_handler),
)