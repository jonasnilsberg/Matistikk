from django.conf.urls import url
from . import views

app_name = 'administration'
urlpatterns = [
    # /maths/
    #url(r'^$', views.IndexView, name='index'),
    url(r'^administration/$', views.StudentCreateView.as_view(), name='createStudent'),
    url(r'^$', views.LoginView.as_view(), name='login'),
]