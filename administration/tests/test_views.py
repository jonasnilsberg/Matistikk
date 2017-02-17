import pytest
from django.test import RequestFactory
from .. import views
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestPersonListView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        usrobj = mixer.blend('administration.Person', role=3)
        req.user = usrobj
        resp = views.PersonListView.as_view()(req)
        import pdb;
        pdb.set_trace()
        assert resp.status_code == 200, 'Should be callable by anyone'