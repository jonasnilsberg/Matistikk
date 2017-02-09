import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db
import ipdb;

class TestSchool:
    def test_init(self):
        obj = mixer.blend('administration.School')
        assert obj.pk == 1, 'Should save an instance'

    def test_get_absolute_url(self):
        obj = mixer.blend('administration.School')
        response = obj.get_absolute_url()
        assert 'skoler/1' in response

class TestGrade:
    def test_init(self):
        obj = mixer.blend('administration.Grade')
        assert obj.pk == 1, 'Should save an instance'

class TestPerson:
    def test_init(self):
        schoolObj = mixer.blend('administration.School', school_name = 'teSkole')
        gradeObj = mixer.blend('administration.Grade', school = schoolObj)
        obj = mixer.blend('administration.Person', grade = gradeObj)
        assert obj.pk == 1, 'should save an instance'

    def test_createUsername(self):
        obj = mixer.blend('administration.Person',first_name='Test',last_name='Testesen')
        assert obj.createusername() == 'testt', 'Should give obj the username "testt"'
        obj2 = mixer.blend('administration.Person',first_name='Test',last_name='Testesen')
        obj2.createusername()
        ipdb.set_trace()
