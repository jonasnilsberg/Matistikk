from django import forms
from .models import Person, Grade, School
from django.core.exceptions import ValidationError

from django.urls import reverse
from django.http import HttpResponseForbidden
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin


class PersonForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'sex', 'is_staff', 'is_active', 'role', 'grades']


class FileUpload(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(FileUpload, self).__init__(*args, **kwargs)
        self.fields['file'].help_text = 'Aksepterte filformat: .xls, .xlsx, .ods, .csv'


class ChangePassword(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Person
        fields = ['password']
        
        
class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['school_name', 'school_address', 'school_administrator']

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['school_administrator'].queryset = Person.objects.filter(role=3)
