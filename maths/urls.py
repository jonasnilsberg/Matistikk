from django.conf.urls import url
from . import views

app_name = 'maths'
urlpatterns = [
    # /matistikk/
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'nyoppgave/$', views.CreateTaskView.as_view(), name='createTask'),

]