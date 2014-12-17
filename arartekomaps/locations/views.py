# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from arartekomaps.settings import STATIC_URL
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place
from arartekomaps.categories.models import Category
from django.core.paginator import Paginator
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
    cities = Location.objects.filter(parent=mystate).order_by('name')
    city_slices = split_seq(cities, 4)
    hidesearch = True
    return render_to_response('listing.html', locals(), context_instance=RequestContext(request)
    )
    
def location(request,state,city,maincat='',subcat=''):
    """ Default view for a city """

    pagenumber = request.GET.get('page','1')
    if int(pagenumber)<1:
        pagenumber = 1
    
    city = get_object_or_404(Location, slug=city)

    rootcats = []
    subcats = []
    places_here = Place.objects.filter(city=city,is_public=True)
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
            pagetitle = _("%(parentcatname)s: %(childcatname)s in %(cityname)s") % {'parentcatname': parentcat.name, 'childcatname': childcat.name, 'cityname': city.name}
            places = Place.objects.filter(city=city, category=childcat,is_public=True)
        else:    
            parentcat = get_object_or_404(Category, slug=maincat)
            pagetitle = _("%(parentcatname)s in %(cityname)s") % {'parentcatname': parentcat.name, 'cityname':city.name}
            places = Place.objects.filter(city=city, is_public=True, category__in=parentcat.get_descendants(include_self=True))
        pass
    else:
        places = Place.objects.filter(city=city,is_public=True)
        pagetitle = city.name     

    pages = Paginator(places,10)
    try:
        thispage = pages.page(int(pagenumber))
    except:
        raise Http404

    p_places = thispage.object_list

    prev_pars = request.GET.copy()
    next_pars = request.GET.copy()
    if pagenumber == '1':
        prev_pars.update({'page':'1'})
    else:
        prev_pars.update({'page':thispage.previous_page_number()})
    try:
        next_pars.update({'page':thispage.next_page_number()})
    except:
        next_pars.update({'page':'1'})
    prev_url = "/filter/?%s" % "&".join(["%s=%s" % (k,v) for k,v in prev_pars.items()])
    next_url = "/filter/?%s" % "&".join(["%s=%s" % (k,v) for k,v in next_pars.items()])

    if pagenumber == '1':
        prev_url = "%s?page=%d" % (request.path,1)
    else:
        prev_url = "%s?page=%d" % (request.path,thispage.previous_page_number())
    try:
        next_url = "%s?page=%d" % (request.path,thispage.next_page_number())
    except:
        next_url = "%s?page=%d" % (request.path,1)
    return render_to_response('location.html', locals(), context_instance=RequestContext(request)
    )