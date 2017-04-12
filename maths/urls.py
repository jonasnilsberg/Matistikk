from django.conf.urls import url
from . import views

app_name = 'maths'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'nyoppgave/$', views.CreateTaskView.as_view(), name='createTask'),
    url(r'equationEditor/$', views.equationEditor.as_view(), name='equationEditor'),
    url(r'oppgaver/$', views.TaskListView.as_view(), name='taskList'),
    url(r'oppgaver/oppdater/(?P<task_pk>[0-9]+)/$', views.TaskUpdateView.as_view(), name='taskUpdate'),
    url(r'kategorier/$', views.CategoryListView.as_view(), name='categoryList'),
    url(r'kategorier/ny/$', views.CategoryCreateView.as_view(), name='categoryCreate'),
    url(r'kategorier/(?P<category_pk>[0-9]+)/oppdater/$', views.CategoryUpdateView.as_view(), name='categoryUpdate'),
    url(r'lagtest/$', views.TaskCollectionCreateView.as_view(), name='taskCollectionCreate'),
    url(r'tester/$', views.TaskCollectionListView.as_view(), name='taskCollectionList'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/$', views.TaskCollectionDetailView.as_view(),
        name='taskCollectionDetail'),
    url(r'tester/publisert/(?P<test_pk>[0-9]+)/$', views.TestDetailView.as_view(), name='testDetail'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/publiser/$', views.TestCreateView.as_view(), name='testCreate'),

]
