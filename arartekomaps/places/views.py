from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from arartekomaps.settings import STATIC_URL
from arartekomaps.locations.models import Location
from arartekomaps.places.models import Place, MPhoto
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datetime import datetime
from arartekomaps.utils.load_images import handle_photo_file
from arartekomaps.mycomment.forms import CommentForm
from arartekomaps.mycomment.models import Comment

def placeview(request, slug=''):
    """ """

    template_name='place'
    users = []
    place = get_object_or_404(Place, slug=slug)
    if MPhoto.objects.filter(place=place, def_img=True).exists():
        def_images = MPhoto.objects.filter(place=place, def_img=True)
    images = MPhoto.objects.filter(place=place,def_img=False).order_by('user')
    username = None
    imgs = []  
    for i, image in enumerate(images):
        if not users:
            username = image.user
            imgs.append(image)
        elif username == image.user:
            imgs.append(image)     
        else:
            users.append({'user': username, 'images': imgs})
            imgs = image
            username = image.user
        if i == len(images)-1:
            users.append({'user': username, 'images': imgs})

    if request.method == 'POST':
        kopia=request.POST.copy()
        kopia['author_id']=request.user.id
        kopia['is_public']=True
        form = CommentForm(kopia)
        if form.is_valid():
              comment = Comment()
              comment.author = request.user
              comment.is_public = True
              comment.public_date = datetime.today()  
              comment.parent = place     
              comment.body = form.cleaned_data['body']
              comment.ip_address = request.META.get("REMOTE_ADDR", None)
              if request.FILES.get('photo',''):
                 photo = handle_photo_file(request.FILES['photo'], request.user.username)              
                 comment.photo= photo
              comment.save()
    form = CommentForm()
    comments = Comment.objects.filter(parent=place,is_public=True,is_deleted=False)

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

