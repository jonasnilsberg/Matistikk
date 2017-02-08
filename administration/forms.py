from django import forms
from .models import Person
from django.core.exceptions import ValidationError

my_default_errors = {
    'required': 'Testing',
    'invalid': 'Enter a valid value'
}


class PersonForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'sex', 'grade', 'is_staff']


class FileUpload(forms.Form):
    file = forms.FileField(label="Last opp en CSV-fil med elever", )
