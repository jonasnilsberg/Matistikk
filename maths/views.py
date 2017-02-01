from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
# Create your views here.


class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/'
    template_name = 'maths/base.html'


