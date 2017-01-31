from django.views.generic import CreateView, View, TemplateView, FormView
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from .models import Person
from matistikk import settings
from .forms import LoginForm
# Create your views here.


class StudentCreateView(CreateView):
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['grade', 'sex', 'first_name', 'username', 'last_name', 'is_staff', 'email']


class LoginView(FormView):
    template_name = 'administration/login.html'
    form_class = AuthenticationForm
    success_url = 'administration'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())



class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(settings.LOGIN_URL)