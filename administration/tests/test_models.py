import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db
from ..models import *


class TestSchool:
    def test_save_delete(self):
        obj = mixer.blend('administration.School')
        obj.save()
        assert len(School.objects.all()) == 1
        obj.delete()
        assert len(School.objects.all()) == 0

    def test_get_absolute_url(self):
        obj = mixer.blend('administration.School')
        response = obj.get_absolute_url()
        assert 'skoler/1' in response


class TestGrade:
    def test_save_delete(self):
        obj = mixer.blend('administration.Grade')
        obj.save()
        assert len(Grade.objects.all()) == 1
        obj.delete()
        assert len(Grade.objects.all()) == 0


class TestPerson:

    def test_save_delete(self):
        obj = mixer.blend('administration.Person')
        obj.save()
        assert len(Person.objects.all()) == 1, 'Should be a saved person object in the database'
        obj.delete()
        assert len(Person.objects.all()) == 0, 'Should be no Person objects in the database'

    def test_createUsername(self):
        modeller = mixer.cycle(3).blend('administration.Person', first_name='T', last_name='AA')
        assert modeller[0].createusername() == 'ta', 'Should return obj the username "ta"'
        modeller[0].username = modeller[0].createusername()
        modeller[0].save()
        modeller[1].username = modeller[1].createusername()
        modeller[1].save()
        modeller[2].username = modeller[1].createusername()
        modeller[2].save()
        assert modeller[0].first_name == modeller[1].first_name, 'First name should be equal for both objects'
        assert modeller[0].last_name == modeller[1].last_name, 'Last name should be equal for both objects'
        assert modeller[0].username != modeller[1].createusername(), 'Usernames should be different'
        assert modeller[2].username == 'taa1', 'Should have the iterative username "taa1"'

    def test_person_grade_school(helskole):
        scObj = mixer.blend('administration.School', school_name='Schoolname')
        grObj = mixer.blend('administration.Grade', school=scObj, grade_name='Gradename')
        prObj = mixer.blend('administration.Person', grade=grObj, first_name='Test', last_name='Testesen')
        prObj.createusername()
        assert prObj.grade.school.school_name == 'Schoolname', 'Should be Schoolname as given in line of the test'

    def test_get_absolute_url(self):
        obj = mixer.blend('administration.Person', username='usrnm')
        response = obj.get_absolute_url()
        assert 'usrnm' in response, 'Url should contain username'
