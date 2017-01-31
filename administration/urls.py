from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    # /maths/
    #url(r'^$', views.IndexView, name='index'),
    url(r'^$', views.StudentCreateView.as_view(), name='createStudent'),

]