from django.views import generic
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin
from .models import Person
# Create your views here.


class PersonListView(StaffuserRequiredMixin, generic.ListView):
    """
       Class to list all the persons
       If the user is staff only students will show
    """
    login_url = '/'
    template_name = 'administration/person_list.html'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Person.objects.filter(is_staff=False, is_superuser=False)
        else:
            return Person.objects.all()


class PersonDetailView(StaffuserRequiredMixin, generic.DetailView):
    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"


class PersonCreateView(StaffuserRequiredMixin, generic.CreateView):
    login_url = '/'
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'grade']
    success_url = '/administration/getallusers'

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





