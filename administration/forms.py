from django.contrib.auth.models import User
from django import forms
from .models import Person


class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_check = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Person
        fields = ['password']
