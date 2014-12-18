from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from arartekomaps.settings import STATIC_URL
from arartekomaps.places.models import Place, Location, Category
from django.core.paginator import Paginator
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

ACCESS_CHOICES = (
        ('', _('Any')),
        ('p', _('Practicable')),
        ('a', _('Accesible')),
    )

ACCESS_AREAS = (
    (_('aphysic'), 'aphysic'),
    (_('avisual'), 'avisual'),
    (_('aaudio'), 'aaudio'),
    (_('aintelec'), 'aintelec'),
    (_('aorganic'), 'aorganic')
)


def home(request):
    """"""
    template_name = 'home'
    hidesearch = True
    places = Place.objects.filter(is_public=True).order_by('?')[:5]
    return render_to_response('home.html',
        locals(), context_instance=RequestContext(request))


def filter(request):
    """ """
    hidesearch = True
    action = 'filter'

    places = Place.objects.filter(is_public=True)

    # City
    try:
        city = int(request.GET.get('city', 0))
        if city:
            city_obj = Location.objects.get(pk=city)
            places = places.filter(city=city_obj)
    except:
        pass

    # Category
    try:
        cat = int(request.GET.get('cat',0))
        if cat:
            cat_obj = Category.objects.get(pk=cat)
            places = places.filter(category__in=cat_obj.get_descendants(include_self=True))
    except:
        pass

    # Accessibility
    ac_form_set = []
    for v,k in ACCESS_AREAS:
        locals()[k] = request.GET.get(k,'')
        optline = []
        for ka,ube in ACCESS_CHOICES:
            if locals()[k] and locals()[k]==ka:
                optline.append((ka,ube,1))
                if ka=='a':
                    places = places.filter(**{'access__%s' % str(k):'a'})
                elif ka=='p':
                    places = places.filter(**{'access__%s__in' % str(k):['a','p']}
                    )
            else:
                optline.append((ka,ube,0))
        ac_form_set.append((k,v,optline))

    pagenumber = request.GET.get('page','1')
    if int(pagenumber)<1:
        pagenumber = 1

    results_number = len(places)

    # data for advanced form
    all_locations = []
    top_locs = Location.objects.filter(level=1).order_by('name')
    for prov in top_locs:
        locs = Location.objects.filter(parent=prov).order_by('name')
        all_locations.append((prov,locs))
    all_cats = Category.objects.filter(level=0)


    access_areas = ACCESS_AREAS
    access_choices = ACCESS_CHOICES

    pages = Paginator(places,10)
    thispage = pages.page(int(pagenumber))
    pins = thispage.object_list


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

    return render_to_response('search.html', locals(), context_instance=RequestContext(request))

def search(request):
    """ """
    hidesearch = True
    action = 'search'

    q = request.GET.get('q','')
    locations = Location.objects.filter(name__search=q)
    all_items = [loc for loc in locations]

    # q
    if q:
        places = Place.objects.filter(name__search=q, is_public=True)
    else:
        places = []

    pagenumber = request.GET.get('page','1')
    if int(pagenumber)<1:
        pagenumber = 1

    all_items.extend(places)
    results_number = len(all_items)

    # data for advanced form

    pages = Paginator(all_items,10)
    thispage = pages.page(int(pagenumber))


    pins = thispage.object_list

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
    prev_url = "/search/?%s" % "&".join(["%s=%s" % (k,v) for k,v in prev_pars.items()])
    next_url = "/search/?%s" % "&".join(["%s=%s" % (k,v) for k,v in next_pars.items()])

    return render_to_response('search.html', locals(), context_instance=RequestContext(request))

def set_language(request):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = redirect(next)
    if request.method == 'GET':
        lang_code = request.GET.get('language', None)
        print lang_code
        if lang_code:
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
    return response

def useroptions(request):
    return render_to_response('useroptions.html', locals(), context_instance=RequestContext(request))

def gsearch(request):
    q = request.GET.get('q','')
    hidesearch = True
    action = 'search'
    return render_to_response('gsearch.html', locals(), context_instance=RequestContext(request))