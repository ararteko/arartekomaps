from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.contrib import admin
from settings import MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'arartekomaps.views.home', name='home'),
    (r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /u/login ", mimetype="text/plain")),
    url(r'^set_lang/$', 'arartekomaps.views.set_language', name='set_lang'),

    url(r'^p/save_location/$', 'arartekomaps.places.views.save_location', name='savelocation'),
    url(r'^p/(?P<slug>[^/]+)/$', 'arartekomaps.places.views.placeview', name='place'),
    url(r'^p/(?P<slug>[^/]+)/locateme$', 'arartekomaps.places.views.locateme', name='locateme'),
    url(r'^p/(?P<slug>[^/]+)/addphoto/$', 'arartekomaps.places.views.addPhoto', name='addPhoto'),

    # url(r'^search/$', 'arartekomaps.views.search', name='search'),
    url(r'^gsearch/$','arartekomaps.views.gsearch',name='gsearch'),

    url(r'^filter/$', 'arartekomaps.views.filter', name='filter'),

    url(r'^l/', include('arartekomaps.locations.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^u/$','django.contrib.auth.views.login', name='erabiltzailea_user_login'),
    url(r'^u/my_places/$','arartekomaps.places.views.my_places', name='edit_places'),
    url(r'^u/new_place/$','arartekomaps.places.views.new_place', name='new_place'),
    url(r'^u/delete_place/(?P<slug>[^/]+)/$','arartekomaps.places.views.delete_place', name='delete_place'),
    url(r'^u/edit_place/(?P<slug>[^/]+)/$','arartekomaps.places.views.edit_place', name='edit_place'),

    (r'^u/', include('cssocialuser.urls')),
    (r'^photologue/', include('photologue.urls')),

    (r'^api/', include('arartekomaps.api.urls')),

    url(r'^pg/', include('pages.urls')),
    (r'^media/places/$', 'django.views.static.serve',{'document_root': MEDIA_ROOT+'/places/'}),
    (r'^media/places/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT+'/places/'}),
)

urlpatterns += staticfiles_urlpatterns()