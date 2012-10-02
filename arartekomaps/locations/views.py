# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from arartekomaps.settings import STATIC_URL
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place
from arartekomaps.categories.models import Category
from django.utils.translation import ugettext_lazy as _


def split_seq(seq, num_pieces):
    """ Split a list in n groups. Useful for listings in cols """
    start = 0
    for i in xrange(num_pieces):
        stop = start + len(seq[i::num_pieces])
        yield seq[start:stop]
        start = stop


def listing(request, state):
    """ Listing cities in an state (probintziak) """
    mystate = Location.objects.get(slug=state)
    cities = Location.objects.filter(parent=mystate)
    city_slices = split_seq(cities, 4)
    hidesearch = True
    return render_to_response('listing.html', locals(), context_instance=RequestContext(request)
    )
    
def location(request,state,city,maincat='',subcat=''):
    """ Default view for a city """
    
    city = get_object_or_404(Location, slug=city)

    rootcats = []
    subcats = []
    places_here = Place.objects.filter(city=city)
    for mplace in places_here:
        thiscat = mplace.category
        rootcat = thiscat.get_root()
        if rootcat not in rootcats:
            rootcats.append(rootcat)
        if maincat and maincat==rootcat.slug and thiscat.get_level()>0 and not thiscat in subcats:
            subcats.append(thiscat)

    if maincat:
        if subcat:
            parentcat = get_object_or_404(Category, slug=maincat) 
            childcat = get_object_or_404(Category, slug=subcat)
            pagetitle = _("%(parentcatname)s: %(childcatname)s in %(cityname)s") % {'parentcatname':_('cat_%s' % parentcat.name), 'childcatname':_('cat_%s' % childcat.name), 'cityname':city.name}
            places = Place.objects.filter(city=city, category=childcat)[:20]
        else:    
            parentcat = get_object_or_404(Category, slug=maincat)
            pagetitle = _("%(parentcatname)s in %(cityname)s") % {'parentcatname':_('cat_%s' % parentcat.name), 'cityname':city.name}
            places = Place.objects.filter(city=city, category__in=parentcat.get_descendants(include_self=True))[:20]
        pass
    else:
        places = Place.objects.filter(city=city)[:20]
        pagetitle = city.name     
        
            
    return render_to_response('location.html', locals(), context_instance=RequestContext(request)
    )