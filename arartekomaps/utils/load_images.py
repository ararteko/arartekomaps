from arartekomaps.places.models import MPhoto
from urllib2 import urlopen
from django.core.files.base import ContentFile


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
    """ """
    if not url:
        url = 'http://irudiak.argazkiak.org/1d3023545b4051907e533648e66329f8_c.jpg'
        name = 'Kakalardoa'

    if " " in url:
        #import pdb
        #pdb.set_trace()
        a=1
    image = _getUrlImage(url)

    if not image:
        return 0

    photo = MPhoto()
    photo.name = name[:100]
    photo.place = place
    
    image_t = Image.open(ContentFile(image.read()))
    image_t = image_t.convert("RGB")
    f=StringIO()
    image_t.save(f,"JPEG")
    f.seek(0)    
    
    unique_slug = url.split('/')[-1].replace(' ','_')
    
    photo.image.save(unique_slug, ContentFile(f.read()))
        
    try:
        a = 3
    except Exception, e:
        print 'Errorea irudi honekin RGB', photo.name, e
        return photo      

    try:
        photo.save()
    except:
        print 'Errorea irudi honekin', photo.name

    return photo
    
    
def handle_uploaded_file(f,name):
    """ """
    photo = MPhoto()
    photo.title = name 
    photo.image = f
    photo.save()
    return photo    
    