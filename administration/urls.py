from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/minside/$', views.MyPageDetailView.as_view(), name='myPage'),
    url(r'nybruker/$', views.PersonCreateView.as_view(), name='personCreate'),
    url(r'brukere/$', views.PersonListView.as_view(), name='personList'),
    url(r'brukere/(?P<slug>[\w-]+)/$', views.PersonDetailView.as_view(), name="personDetail"),
    url(r'brukere/oppdater/(?P<slug>[\w-]+)/$', views.PersonUpdateView.as_view(), name='personUpdate'),
    url(r'skoler/$', views.SchoolListView.as_view(), name='schoolList'),
    url(r'skoler/(?P<pk>[0-9]+)/$', views.SchoolDetailView.as_view(), name="schoolDetail"),
    url(r'lagskole/$', views.SchoolCreateView.as_view(), name='schoolCreate'),
    url(r'skoler/oppdater/(?P<pk>[0-9]+)/$', views.SchoolUpdateView.as_view(), name='schoolUpdate'),
    url(r'skoler/oppdater/(?P<pk>[0-9]+)/leggtilklasse/$', views.GradeCreateView.as_view(), name='gradeCreate'),
    url(r'skoler/(?P<school_pk>[0-9]+)/klasse/(?P<pk>[0-9]+)/$', views.GradeDetailView.as_view(), name='gradeDetail'),
    url(r'skoler/(?P<school_pk>[0-9]+)/klasse/(?P<pk>[0-9]+)/oppdater/$', views.GradeUpdateView.as_view(),
        name='gradeUpdate'),
    url(r'skoler/(?P<school_pk>[0-9]+)/klasse/(?P<pk>[0-9]+)/elev/$', views.PersonCreateView.as_view(),
        name='gradeAddStudent'),
    url(r'skoler/(?P<school_pk>[0-9]+)/grade/(?P<pk>[0-9]+)/lærer/$', views.PersonCreateView.as_view(role=2),
        name='gradeAddTeacher'),
    url(r'mineklasser/$', views.GradeListView.as_view(), name='gradeList')
    # url(r'getallusers/search', views.PersonSearch.as_view(), name='personSearch')
]
