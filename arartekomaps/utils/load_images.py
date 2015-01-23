from arartekomaps.places.models import MPhoto
from photologue.models import Photo
from urllib2 import urlopen
from django.core.files.base import ContentFile
from arartekomaps.utils.slug import time_slug, time_slug_long, time_slug_string

from cStringIO import StringIO
try:
    from PIL import Image
except ImportError:
    import Image

import socket
socket.setdefaulttimeout(20)
import cgi

def _getUrlImage(url):
    """ """    
    url1 = url.replace(' ','%20')
    try:
        mysocket = urlopen(url1)
    except:
        mysocket = None
    return mysocket


def loadUrlImage(url, place, name='', format='jpg'):
    """ 
    Only called from importers. Be aware that we overwrite an image if
    it exists!!
    """
    
    image = _getUrlImage(url)

    if not image:
        return 0

    photos = MPhoto.objects.filter(place=place)
    if len(photos)>0:
        photo = photos[0]
    else:
        photo = MPhoto()

    photo.name = name[:100]
    photo.place = place
    photo.def_img = True
    
    try:
        image_t = Image.open(ContentFile(image.read()))
    except:
        return photo
    image_t = image_t.convert("RGB")
    f=StringIO()
    image_t.save(f,"JPEG")
    f.seek(0)    
    
    unique_slug = url.split('/')[-1].replace(' ','_')
    
    photo.image.save(unique_slug, ContentFile(f.read()))

    try:
        photo.save()
    except:
        print 'Error with this image', photo.name

    return photo
    
    
def handle_uploaded_file(f,name):
    """ """
    photo = MPhoto()
    photo.title = name 
    photo.image = f
    photo.save()
    return photo

def handle_photo_file(f,title):
    """ """
    photo = Photo()
    photo.title = u'%s %s' % (time_slug_string(), title) 
    photo.title_slug = time_slug_string()
    photo.image = f
    photo.save()
    return photo
    