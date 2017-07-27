from django.conf.urls import url
from . import views

app_name = 'maths'
urlpatterns = [

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'nyoppgave/$', views.TaskCreateView.as_view(), name='createTask'),
    url(r'equationEditor/$', views.EquationEditorView.as_view(), name='equationEditor'),
    url(r'oppgaver/$', views.TaskListView.as_view(), name='taskList'),
    url(r'oppgaver/(?P<task_pk>[0-9]+)/$', views.TaskDetailView.as_view(), name='taskDetail'),
    url(r'oppgaver/oppdater/(?P<task_pk>[0-9]+)/$', views.TaskUpdateView.as_view(), name='taskUpdate'),
    url(r'kategorier/$', views.CategoryListView.as_view(), name='categoryList'),
    url(r'kategorier/ny/$', views.CategoryCreateView.as_view(), name='categoryCreate'),
    url(r'kategorier/(?P<category_pk>[0-9]+)/oppdater/$', views.CategoryUpdateView.as_view(), name='categoryUpdate'),
    url(r'lagtest/$', views.TaskCollectionCreateView.as_view(), name='taskCollectionCreate'),
    url(r'tester/$', views.TaskCollectionListView.as_view(), name='taskCollectionList'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/$', views.TaskCollectionDetailView.as_view(),
        name='taskCollectionDetail'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/oppdater/$', views.TaskCollectionUpdateView.as_view(),
        name='taskCollectionUpdate'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/slett/$', views.TaskCollectionDeleteView.as_view(),
        name='taskCollectionDelete'),
    url(r'minetester/(?P<slug>[\w-]+)/$', views.TestListView.as_view(), name='testList'),
    url(r'minetester/(?P<slug>[\w-]+)/publiser/(?P<test_pk>[0-9]+)/$', views.TestListView.as_view(),
        name='testListPublish'),
    url(r'tester/publisert/(?P<test_pk>[0-9]+)/slett/$', views.TestDeleteView.as_view(), name='testDelete'),
    url(r'tester/publisert/(?P<test_pk>[0-9]+)/$', views.TestDetailView.as_view(), name='testDetail'),
    url(r'tester/publisert/(?P<test_pk>[0-9]+)/(?P<grade_pk>[0-9]+)/klasse/$', views.TestDetailView.as_view(),
        name='testGradeDetail'),
    url(r'tester/publisert/(?P<test_pk>[0-9]+)/(?P<group_pk>[0-9]+)/gruppe/$', views.TestDetailView.as_view(),
        name='testGroupDetail'),
    url(r'tester/(?P<taskCollection_pk>[0-9]+)/publiser/$', views.TestCreateView.as_view(), name='testCreate'),
    url(r'test/(?P<test_pk>[0-9]+)/besvarelse/(?P<slug>[\w-]+)/$', views.AnswerListView.as_view(), name='answerDetail'),
    url(r'test/(?P<test_pk>[0-9]+)/besvarelse/public/(?P<user_id>[0-9]+)/$', views.AnswerListView.as_view(),
        name='answerDetailAnonymous'),
    url(r'test/(?P<test_pk>[0-9]+)/svar/$', views.AnswerCreateView.as_view(), name='answerCreate'),
    url(r'test/(?P<test_pk>[0-9]+)/eksporter/$', views.export_data, name='answerExport'),
    url(r'test/fullført/$', views.LinkSuccess.as_view(), name='answerFinished'),
    url(r'eksportering/$', views.ExportData.as_view(), name='exportData')

]
