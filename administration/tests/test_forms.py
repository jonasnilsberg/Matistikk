import pytest
from .. import forms
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestPersonForm:
    def test_empty(self):
        form = forms.PersonForm(data={})
        assert form.is_valid() is False, 'Should be invalid when no data is given'

    def test_all_required_values(self):
        obj = mixer.blend('administration.Person')  # gives the object random values
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': obj.date_of_birth,
                'sex': obj.sex}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when given first_name, last_name, date_of_birth and sex'

    def test_all_values_given(self):
        gradeObj = mixer.blend('administration.Grade', grade_name='Gradename')
        gradeObj.save()
        obj = mixer.blend('administration.Person')  # gives the object random values
        obj.save()
        # data={'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': '13.10.1995', 'sex': obj.sex, 'email': obj.email, 'grades': obj.grades, 'is_staff' : obj.is_staff, 'is_active':True}
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': obj.date_of_birth,
                'sex': obj.sex, 'email': obj.email, 'grades': obj.grades.all(), 'is_staff': False, 'is_active': True}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when given all fields'