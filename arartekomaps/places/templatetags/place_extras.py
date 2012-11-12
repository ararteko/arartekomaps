from django.template.defaultfilters import stringfilter

from django import template
register = template.Library()

@register.filter(name='normaltxo')
@stringfilter
def normaltxo(value):
    trans = {'Frantzisko':'Franzisko',
             'Inazio':'Ignazio',
             'Miguel Urruzuno':'Migel Urruzuno',
             'Ermuaranbide':'Ermuaran',
             'Lorenzo':'Lorentzo'}
    for k,v in trans.items():
        value = value.replace(k,v)
    return value


@register.filter(name='get_username')
def get_username(images):
    image = images[0]
    return image.user.get_full_name()