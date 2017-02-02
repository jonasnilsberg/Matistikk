from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    url(r'createuser/$', views.PersonCreateView.as_view(), name='createPerson'),
    url(r'getallusers/$', views.PersonListView.as_view(), name='personList'),
    url(r'getallusers/(?P<slug>[\w-]+)/$', views.PersonDetailView.as_view(), name="personDetail"),
    url(r'getallusers/update/(?P<slug>[\w-]+)/$', views.PersonUpdateView.as_view(), name='personUpdate'),
    url(r'allschools/$', views.SchoolListView.as_view(), name='schoolList'),
    url(r'allschools/(?P<pk>[0-9]+)/$', views.SchoolDetailView.as_view(), name="schoolDetail"),
]