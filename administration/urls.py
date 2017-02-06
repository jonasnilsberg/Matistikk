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
    url(r'createschool/$', views.SchoolCreateView.as_view(), name='schoolCreate'),
    url(r'allschools/update/(?P<pk>[0-9]+)/$', views.SchoolUpdateView.as_view(), name='schoolUpdate'),
    url(r'allschools/update/(?P<pk>[0-9]+)/addgrade/$', views.GradeCreateView.as_view(), name='gradeCreate'),
    url(r'allschools/(?P<school_pk>[0-9]+)/grade/(?P<pk>[0-9]+)/$', views.GradeDetailView.as_view(), name='gradeDetail'),
    url(r'allschools/(?P<school_pk>[0-9]+)/grade/(?P<pk>[0-9]+)/update/$', views.GradeUpdateView.as_view(),
        name='gradeUpdate'),
    url(r'allschools/(?P<school_pk>[0-9]+)/grade/(?P<pk>[0-9]+)/addStudent/$', views.PersonCreateView.as_view(),
        name='gradeAddStudent'),
    url(r'allschools/(?P<school_pk>[0-9]+)/grade/(?P<pk>[0-9]+)/addTeacher/$', views.PersonCreateView.as_view(is_staff=True),
        name='gradeAddTeacher'),

    # url(r'getallusers/search', views.PersonSearch.as_view(), name='personSearch')
]