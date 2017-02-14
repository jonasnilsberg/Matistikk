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
                'sex': obj.sex, 'role': obj.role}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when given first_name, last_name, date_of_birth, sex and role'

    def test_all_values_given(self):
        gradeObj = mixer.blend('administration.Grade', grade_name='Gradename')
        gradeObj.save()
        obj = mixer.blend('administration.Person')  # gives the object random values
        obj.save()
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': obj.date_of_birth,
                'sex': obj.sex, 'email': obj.email, 'grades': obj.grades.all(), 'role': obj.role}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when all fields in the form are given'
