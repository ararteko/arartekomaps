from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from arartekomaps.settings import STATIC_URL
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place, MPhoto
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.contrib.comments.forms import CommentForm


def placeview(request, slug=''):
    """ """
    template_name='place'
    place = get_object_or_404(Place, slug=slug)
    images = MPhoto.objects.filter(place=place)
    return render_to_response('place.html', locals(), context_instance=RequestContext(request)
    )

@login_required
def locateme(request, slug=''):
    template_name='locateme'
    place = get_object_or_404(Place, slug=slug)
    if place.lat:
        df_lat, df_lon = place.lat, place.lon
    else:
        df_lat, df_lon = 43.21323021, -2.4114561080
    return render_to_response('locateme.html', locals(), context_instance=RequestContext(request)
    )

@login_required
def save_location(request):
    if request.method == 'POST': # If the form has been submitted...
        place_slug = request.REQUEST['place_slug']
        lat = request.REQUEST['lat']
        lon = request.REQUEST['lon']
        myPlace = get_object_or_404(Place, slug=place_slug)
        myPlace.lat=lat
        myPlace.lon=lon
        myPlace.save()
        return HttpResponseRedirect(myPlace.get_absolute_url()) # Redirect after POST
    else:
        place_slug = request.REQUEST['place_slug']
        if request.REQUEST.has_key('place_slug'):
            myBizi = get_object_or_404(Place, slug=place_slug)
            return HttpResponseRedirect(myPlace.get_absolute_url())
        else:
            return HttpResponseRedirect('/')
            
@login_required
def addPhoto(request, slug=''):
    template_name='addphoto'
    place = get_object_or_404(Place, slug=slug)
    if request.method == 'POST': # If the form has been submitted...
        if request.FILES.get('image',''):    
            photo = MPhoto()
            photo.name = request.REQUEST['name']
            photo.image = request.FILES['image']
            photo.user= request.user
            photo.place = place
            photo.save()
        return HttpResponseRedirect(place.get_absolute_url()) # Redirect after POST
    else:
        return render_to_response('addphoto.html', locals(), context_instance=RequestContext(request)
        )            

