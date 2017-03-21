from django import forms
from .models import Grade, Person, School


class PersonForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')
    ROLE = [
        (1, "Elev"),
        (2, 'Lærer'),
        (3, 'Skoleadministrator'),
        (4, 'Administrator')
    ]
    role = forms.ChoiceField(choices=ROLE, label='Brukertype')

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'sex', 'is_staff', 'is_active', 'grades', 'role']


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
        fields = ['school_name', 'school_address', 'school_administrator', 'is_active']

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['school_administrator'].queryset = Person.objects.filter(role=3)


class SchoolAdministrator(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        model = Person
        fields = ['email', 'date_of_birth', 'sex']
