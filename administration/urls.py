from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    url(r'^$', views.PersonCreateView.as_view(), name='createPerson'),
]