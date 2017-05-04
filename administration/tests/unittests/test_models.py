import pytest
from mixer.backend.django import mixer
from administration.models import *
pytestmark = pytest.mark.django_db


class TestSchool:
    def test_save_delete(self):
        obj = mixer.blend('administration.School')
        obj.save()
        assert len(School.objects.all()) == 1, "There should be a school stored in the database"
        obj.delete()
        assert len(School.objects.all()) == 0, "There should not be a school object stored in the database"

    def test_get_absolute_url(self):
        obj = mixer.blend('administration.School')
        response = obj.get_absolute_url()
        assert 'skoler/' + str(obj.pk) in response, "The correct pk should be in the url"

class TestGrade:
    def test_save_delete(self):
        obj = mixer.blend('administration.Grade')
        obj.save()
        assert len(Grade.objects.all()) == 1, "There should be a Grade object stored in the database"
        obj.delete()
        assert len(Grade.objects.all()) == 0, "There should not be a Grade object stored in the database"


class TestPerson:

    def test_save_delete(self):
        obj = mixer.blend('administration.Person')
        obj.save()
        assert len(Person.objects.all()) == 1, 'Should be a saved person object in the database'
        obj.delete()
        assert len(Person.objects.all()) == 0, 'Should be no Person objects in the database'

    def test_create_username(self):
        modeller = mixer.cycle(3).blend('administration.Person', first_name='T', last_name='AA')
        assert modeller[0].create_username() == 'ta', 'Should return the username "ta"'
        modeller[0].username = modeller[0].create_username()
        modeller[0].save()
        modeller[1].username = modeller[1].create_username()
        modeller[1].save()
        modeller[2].username = modeller[2].create_username()
        modeller[2].save()
        assert modeller[0].first_name == modeller[1].first_name, 'First name should be equal for both objects'
        assert modeller[0].last_name == modeller[1].last_name, 'Last name should be equal for both objects'
        assert modeller[0].username != modeller[1].create_username(), 'Usernames should be different'
        assert modeller[2].username == 'taa1', 'Should have the iterative username "taa1"'

    def test_person_grade_school(self):
        scObj = mixer.blend('administration.School', school_name='Schoolname')
        grObj = mixer.blend('administration.Grade', school=scObj, grade_name='Gradename')
        prObj = mixer.blend('administration.Person', grade=grObj, first_name='Test', last_name='Testesen')
        prObj.create_username()
        assert prObj.grade.school.school_name == 'Schoolname', 'Should be Schoolname as given in line of the test'

    def test_get_absolute_url(self):
        obj = mixer.blend('administration.Person', username='username')
        response = obj.get_absolute_url()
        assert 'username' in response, 'Url should contain username'


class TestGruppe:

    def test_save_delete(self):
        obj = mixer.blend('administration.Gruppe')
        obj.save()
        assert len(Gruppe.objects.all()) == 1, "Should be a Gruppe object in the database"
        obj.delete()
        assert len(Gruppe.objects.all()) == 0, "Should be no Gruppe objects in the database"