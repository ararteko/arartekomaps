from django.conf import settings
from django import forms
from models import Place,Location
from arartekomaps.categories.models import Category
from django.utils.translation import ugettext_lazy as _

class PlaceForm(forms.ModelForm):
    city = forms.ModelChoiceField(label=_('City'),queryset=Location.objects.filter(level=2).order_by('name'), help_text=_('Nombre del municipio'))
    category = forms.ModelChoiceField(label=_('Category'),queryset=Category.objects.filter(parent__isnull=False).order_by('name'), help_text=_('Elige una categoria del lugar'))
    address1 = forms.CharField(label=_('Address'), widget=forms.TextInput(attrs={'size':'20'}), help_text=_('Direccion 1 del lugar'))
    address2 = forms.CharField(label='', widget=forms.TextInput(attrs={'size':'20'}), help_text=_('Direccion 2 del lugar'),required=False)
    afileurl = forms.CharField(label=_('URL externa'), widget=forms.TextInput(attrs={'size':'20'}), help_text=_('Pagina web externa con informacion detallada sobre la accesibilidad del recurso'),required=False)

    class Meta:
        model = Place
        exclude = ('slug','author','description','source','adescription','url','url_name')