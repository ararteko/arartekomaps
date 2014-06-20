from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', RedirectView.as_view(url='/')),
    url(r'^(?P<state>[^/]+)/$', 'arartekomaps.locations.views.listing', name='listing'),
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/(?P<maincat>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),    
    url(r'^(?P<state>[^/]+)/(?P<city>[^/]+)/(?P<maincat>[^/]+)/(?P<subcat>[^/]+)/$', 'arartekomaps.locations.views.location', name='location'),
 
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   

)
