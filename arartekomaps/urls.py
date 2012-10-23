from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import redirect_to
from django.contrib import admin
from settings import MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'arartekomaps.views.home', name='home'),
    url(r'^set_lang/$', 'arartekomaps.views.set_language', name='set_lang'),
    
    url(r'^p/save_location/$', 'arartekomaps.places.views.save_location', name='savelocation'),
    url(r'^p/(?P<slug>[^/]+)/$', 'arartekomaps.places.views.placeview', name='place'),
    url(r'^p/(?P<slug>[^/]+)/locateme$', 'arartekomaps.places.views.locateme', name='locateme'),
    url(r'^p/(?P<slug>[^/]+)/addphoto/$', 'arartekomaps.places.views.addPhoto', name='addPhoto'),
    
    #url(r'^search/$', 'arartekomaps.views.search', name='search'),
    url(r'^bilatzailea/$','arartekomaps.views.bilaketa',name='bilaketa'),    
    
    url(r'^filter/$', 'arartekomaps.views.filter', name='filter'),

    url(r'^l/', include('arartekomaps.locations.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^u/$','django.contrib.auth.views.login', name='erabiltzailea_user_login'),
        
    (r'^u/', include('cssocialprofile.urls')),
    (r'^photologue/', include('photologue.urls')),
    url(r'^pg/', include('pages.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT}),
)

urlpatterns += staticfiles_urlpatterns()
