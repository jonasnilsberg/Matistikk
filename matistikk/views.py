from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.core import validators
from django import forms
from django.forms.forms import NON_FIELD_ERRORS

from django.shortcuts import render


class LoginView(FormView):
    template_name = 'administration/login.html'
    form_class = AuthenticationForm
    success_url = 'maths'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
