from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', redirect_to, {'url': '/'}),
    url(r'^(?P<state>[^/]+)/$', 'arartekomaps.locations.views.listing', name='listing'),
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/(?P<maincat>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),    
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/(?P<maincat>[^/]+)/(?P<subcat>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),
 
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   

)
