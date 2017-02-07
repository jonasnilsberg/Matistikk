from django import forms
from .models import Person
from django.core.exceptions import ValidationError

my_default_errors = {
    'required': 'Testing',
    'invalid': 'Enter a valid value'
}

