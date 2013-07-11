from django import forms
from models import *
from django.utils.translation import ugettext_lazy as _

class CommentForm(forms.Form):
    """ """
    body = forms.CharField(label='',widget=forms.Textarea)
    photo  = forms.ImageField(label=_('Irudia'),help_text=_('Onartutako formatuak: jpg, png, gif.'),required=False)

    def clean_body(self):
        """ """
        body = self.cleaned_data['body'].strip()
        if not body:
            raise forms.ValidationError('Mezu hutsek ez dute balio. Mesedez, idatzi zerbait!')
        return self.cleaned_data['body']
    
    def clean_photo(self):
        """ """
        photo = self.cleaned_data['photo']
        if not photo:
            return None


        name = photo.name
        try:
            name.encode('ascii')
        except:
            raise forms.ValidationError(u'Argazkiaren izenak (%s) karaktere arraroren bat du eta errorea ematen du. Aldatu argazkiari izena, mesedez!' % name)            

        if len(name)>90:
            raise forms.ValidationError(u'Argazkiaren izena (%s) luzeegia da. Aldatu argazkiari izena, mesedez!' % name)            
        

        format = name.split('.')[-1]
        if format.lower().strip() not in (u'jpg',u'png',u'gif'):
            raise forms.ValidationError(_(u'Argazkiaren formatua ez da egokia. Aldatu formatua, mesedez!'))        
      
        return photo

    class Meta:
         model=Comment