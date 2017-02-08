import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db


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
