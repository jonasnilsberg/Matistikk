from django.views import generic
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin
from django.core.paginator import Paginator


from .models import Person, School, Grade
# Create your views here.


class PersonListView(StaffuserRequiredMixin, generic.ListView):
    """
       Class to list all the persons
       If the user is staff only students will show
    """

    login_url = '/'
    template_name = 'administration/person_list.html'
    paginate_by = 20

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Person.objects.filter(is_staff=False, is_superuser=False)
        else:
            return Person.objects.all()


class PersonDetailView(StaffuserRequiredMixin, generic.DetailView):
    """
       Class to list a specific Person based on username
       returns the user to value set in template_name
    """

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


class PersonUpdateView(StaffuserRequiredMixin, generic.UpdateView):
    template_name = 'administration/student_create.html'
    login_url = '/'
    model = Person
    slug_field = "username"
    fields = ['first_name', 'last_name', 'email', 'sex', 'grade']


class SchoolListView(StaffuserRequiredMixin, generic.ListView):
    login_url = '/'
    model = School
    template_name = 'administration/school_list.html'
    paginate_by = 20


class SchoolDetailView(StaffuserRequiredMixin, generic.DetailView):
    model = School
    template_name = 'administration/school_detail.html'
    # slug_field = "username"

    def get_context_data(self, **kwargs):
        context = super(SchoolDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.filter(school_id=self.kwargs['pk'])
        return context








