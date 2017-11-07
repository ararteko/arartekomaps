from django import forms
from models import *
from django.utils.translation import ugettext_lazy as _

class CommentForm(forms.Form):
    """ """
    body = forms.CharField(label='',widget=forms.Textarea)
    photo  = forms.ImageField(label=_('Image'),help_text=_('Accepted formats: jpg, png, gif.'),required=False)

    def clean_body(self):
        """ """
        body = self.cleaned_data['body'].strip()
        if not body:
            raise forms.ValidationError(_('Void messages not accepted. Please, type some text explaining!'))
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
            raise forms.ValidationError(_(u'The name of the file (%s) has an non standard character and cannot be processed. Please rename the image before uploading!') % name)            

        if len(name)>90:
            raise forms.ValidationError(_(u'The name of the file (%s) is too long. Please rename the image before uploading!') % name)            
        

        format = name.split('.')[-1]
        if format.lower().strip() not in (u'jpg',u'png',u'gif'):
            raise forms.ValidationError(_(u'The format of the image is not valid. Please upload an image in an accepted format!'))        
      
        return photo

    class Meta:
         model=Comment
