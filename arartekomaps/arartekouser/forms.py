from django import forms
from arartekomaps.arartekouser.models import ArartekoUser
from django.contrib.auth.forms import PasswordResetForm


class PasswordReset(forms.Form):
    oldpassword = forms.CharField(widget=forms.PasswordInput(),max_length=100)
    password1 = forms.CharField(widget=forms.PasswordInput(),max_length=100)
    password2 = forms.CharField(widget=forms.PasswordInput(),max_length=100)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordReset, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        if self.clean_data.get('oldpassword') and not self.user.check_password(self.clean_data['oldpassword']):
            raise ValidationError('Please type your current password.')
        return self.clean_data['oldpassword']

    def clean_password2(self):
        if self.clean_data.get('password1') and self.clean_data.get('password2') and self.clean_data['password1'] != self.clean_data['password2']:
            raise ValidationError('The new passwords are not the same')
        return self.clean_data['password2']


