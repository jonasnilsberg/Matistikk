from django.views.generic import CreateView, View, TemplateView, FormView
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin
from .models import Person
# Create your views here.


class PersonCreateView(StaffuserRequiredMixin, CreateView):
    login_url = '/'
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'grade']
    success_url = '/maths'

    def form_valid(self, form):
        person = form.save(commit=False)
        # first_name = form.cleaned_data['first_name']
        # last_name = form.cleaned_data['last_name']
        staff = self.request.POST.get('staff')
        if staff:
            person.is_staff = staff
        person.set_password('ntnu123')
        person.save()
        return super(PersonCreateView, self).form_valid(form)





