from django.contrib import admin
from arartekomaps.locations.models import Location
from django import forms
from django.template.loader import render_to_string

class mapWidget(forms.widgets.Input):
    """ """
    input_type = None
    def render(self, name, value, attrs=None):
        return render_to_string('mapwidget.html', locals())

class LocationAdminForm(forms.ModelForm):
    map = forms.CharField(widget=mapWidget(), required=False) 
    class Meta:
        model = Location
        fields = ('name','slug','parent','level','lat','lon','map')

class LocationAdmin(admin.ModelAdmin):
    form = LocationAdminForm
    list_display = ('name','slug','lat','lon')
    readonly_fields = ()
    search_fields = ('name',)
    filter_fields = ('lat',)
    
admin.site.register(Location, LocationAdmin)

