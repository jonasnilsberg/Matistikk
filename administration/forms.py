from django import forms
from .models import Grade, Person, School


class PersonForm(forms.ModelForm):
    """
    Form used to create a new person.

    :First_name: Persons first name.
    :Last_name: Persons last name.
    :Email: Persons email.
    :Date_of_Birth: Persons date of birth.
    :Sex: Persons sex.
    :Is_active: Decides if the Person is active or not. Used instead of deleting the Person.
    :Grades: Which grades the person are in.
    :Role: Persons role in the system.

    """
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        """
            Bases the form on the Person model
        """
        model = Person
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'sex', 'is_active', 'grades', 'role']


class FileUploadForm(forms.Form):
    """
    Form used to upload excel file with Person information.

    :File: The file that will be uploaded.

    """
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        """
            Adds help text to the file field when initiated.
        """
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].help_text = 'Aksepterte filformat: .xls, .xlsx, .ods, .csv'


class ChangePasswordForm(forms.ModelForm):
    """
    Form used to change the password to a Person.

    :Password: New password for the Person.
    :Password2: New repeated password for the Person.

    """

    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """
            Bases the form on the Person model
        """
        model = Person
        fields = ['password']


class SchoolForm(forms.ModelForm):
    """
    Form used to create a school.

    :School_name: Name of the school.
    :School_address: Address of the school.
    :School_administrator: Person responsible for the school.
    :Is_active: Decides if the School is active or not. Used instead of deleting the School.

    """

    class Meta:
        """
        Bases the form on the School model.
        """
        model = School
        fields = ['school_name', 'school_address', 'school_administrator', 'is_active']

    def __init__(self, *args, **kwargs):
        """
        Changes the queryset to only match persons with the role 3, so only school administrators can be appointed.

        """
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['school_administrator'].queryset = Person.objects.filter(role=3)


class SchoolAdministratorForm(forms.ModelForm):
    """
    Form used to create a school administrator.

    :First_name: The school administrators first name.
    :Last_name: The school administrators last name.
    :Email: The school administrators email.
    :Date_of_birth: The school administrators date of birth.
    :Sex: The school administrators sex.
    """
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        """
            Bases the form on the Person model.
        """
        model = Person
        fields = ['email', 'date_of_birth', 'sex']
