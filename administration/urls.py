from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    url(r'createuser/$', views.PersonCreateView.as_view(), name='createPerson'),
    url(r'getallusers/$', views.PersonListView.as_view(), name='personList'),
    url(r"getallusers/(?P<slug>[\w-]+)/$", views.PersonDetailView.as_view(), name="personDetail"),
]