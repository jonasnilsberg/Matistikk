from django.conf.urls import url
from . import views

app_name = 'maths'
urlpatterns = [
    # /matistikk/
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'nyoppgave/$', views.CreateTaskView.as_view(), name='createTask'),
    url(r'oppgaver/$', views.TaskListView.as_view(), name='taskList'),
    url(r'oppgaver/oppdater/(?P<task_pk>[0-9]+)/$', views.TaskUpdateView.as_view(), name='taskUpdate'),
    url(r'kategorier/$', views.CategoryListView.as_view(), name='categoryList'),
    url(r'kategorier/ny/$', views.CategoryCreateView.as_view(), name='categoryCreate'),
    url(r'kategorier/(?P<category_pk>[0-9]+)/oppdater/$', views.CategoryUpdateView.as_view(), name='categoryUpdate'),
    url(r'lagtest/$', views.TestCreateView.as_view(), name='testCreate'),
    url(r'tester/$', views.TestListView.as_view(), name='testList'),
    url(r'tester/(?P<test_pk>[0-9]+)/$', views.TestDetailView.as_view(), name='testDetail'),
    url(r'tester/(?P<test_pk>[0-9]+)/publiser/$', views.TestDisplayCreateView.as_view(), name='testDisplayCreate')
]
