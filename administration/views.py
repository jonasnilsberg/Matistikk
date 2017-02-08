from django.views import generic
from django.views.generic import edit
from braces import views
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Person, School, Grade
from django.shortcuts import render, render_to_response, HttpResponse
from django.http import JsonResponse
from django.contrib import messages

import logging
from django.core import serializers
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from .forms import PersonForm, FileUpload

# Create your views here.


class MyPageDetailView(generic.FormView):
    def test_func(self, user):
        return self.request.user.username == self.kwargs.get('slug')

    form_class = PasswordChangeForm
    slug_field = 'username'
    template_name = 'administration/mypage.html'

    def get_success_url(self):
        return reverse('administration:myPage', kwargs={'slug': self.kwargs.get('slug')})

    def get_form(self, form_class=form_class):
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        person = form.save(commit=False)
        password = form.cleaned_data['new_password1']
        person.set_password(password)
        person.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Passordet ble oppdatert!')
        return super(MyPageDetailView, self).form_valid(form)


class PersonListView(views.StaffuserRequiredMixin, views.AjaxResponseMixin, generic.ListView):
    """
        Class to list all the persons

        If the user is staff only students will show

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.ListView: Inherits generic.ListView that makes a page representing a list of objects.
        :return: List of person objects
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/person_list.html'

    def get_queryset(self):
        """
           Function that Overrides the default queryset from generic.ListView to get the proper Person object list.

           :param self: References to the class itself and all it's variables
           :return: List of person objects
        """
        if not self.request.user.is_superuser:
            return Person.objects.filter(is_staff=False, is_superuser=False)
        else:
            return Person.objects.all()


class PersonDetailView(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Person based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.DetailView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: Person object

    """

    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"


class PersonCreateView(views.StaffuserRequiredMixin,  generic.CreateView):
    """
        Class to create a Person object

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
    """

    login_url = reverse_lazy('login')
    is_staff = False
    template_name = 'administration/person_form.html'
    form_class = PersonForm
    #model = Person
    #fields = ['first_name', 'last_name', 'email', 'sex', 'grade']
    success_url = reverse_lazy('administration:personList')

    def get_initial(self):
        """
            Function that checks for preset Person values and sets the to the field

            :param self: References to the class itself and all it's variables.
            :return: List the preset values
        """

        if self.kwargs.get('pk'):
            self.success_url = reverse_lazy('administration:gradeDetail',
                                            kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'pk': self.kwargs.get('pk')})
            return {'grade': self.kwargs.get('pk'), 'is_staff': self.is_staff}

    def form_valid(self, form):
        """
            Function that overrides the default form_valid so that a password and is_staff can be added if
            necessary.

            :param self: References to the class itself and all it's variables.
            :param form: References to the model form.
            :return: The HttpResponse set in success_url.
        """
        first_name_form = form.cleaned_data['first_name']
        last_name_form = form.cleaned_data['last_name']
        first_name = first_name_form.replace(" ", "")
        first_name_lower = first_name.lower()
        last_name_lower = last_name_form.lower()
        last_name_tab = str.split(last_name_lower)
        username = first_name_lower
        for letter in last_name_tab:
            username += letter[0]
        person = form.save(commit=False)
        last_name_list = list(last_name_tab[-1])
        for letter in last_name_list[1:]:
            if Person.objects.filter(username__exact=username):
                username += letter
            else:
                person.username = username
                break
        counter = 1
        username_correct = username
        while Person.objects.filter(username__exact=username_correct):
            username_correct = username + str(counter)
            counter +=1
        person.username = username_correct
        person.set_password('ntnu123')
        person.save()
        return super(PersonCreateView, self).form_valid(form)


class PersonUpdateView(views.StaffuserRequiredMixin, generic.UpdateView):
    """
        Class to update a Person object based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in
            as staff
        :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
            saving the form when validated.
        :return: The HttpResponse set in success_url
    """

    template_name = 'administration/person_form.html'
    login_url = reverse_lazy('login')
    form_class = PersonForm
    model = Person
    slug_field = "username"


class SchoolListView(views.StaffuserRequiredMixin, generic.ListView):
    """
        Class to list out all School objects

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.ListView: Inherits generic.ListView that represents a page containing a list of objects
        :return: List of School objects

    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_list.html'
    paginate_by = 20


class SchoolDetailView(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Person based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.UpdateView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: School object

    """
    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SchoolDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.filter(school_id=self.kwargs['pk'])
        return context


class SchoolCreateView(views.SuperuserRequiredMixin, generic.CreateView):
    """
        Class to create a School object

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
        :return: The HttpResponse set in success_url
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/school_form.html'
    model = School
    fields = ['school_name', 'school_address']
    success_url = reverse_lazy('administration:schoolList')


class SchoolUpdateView(views.SuperuserRequiredMixin, generic.UpdateView):
    """
        Class to update a School object based on the school.id

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a object and
            saving the form when validated.
        :return: The HttpResponse set in success_url
    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_form.html'
    fields = ['school_name', 'school_address']


class GradeDetailView(views.StaffuserRequiredMixin,edit.FormMixin, generic.DetailView):
    """
        Class to get a specific Grade based on the grade.id

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.UpdateView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: School object
    """
    form_class = FileUpload
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GradeDetailView, self).get_context_data(**kwargs)
        context['students'] = Person.objects.filter(grade_id=self.kwargs['pk'], is_staff=False)
        context['teachers'] = Person.objects.filter(grade_id=self.kwargs['pk'], is_staff=True)
        context['form'] = self.get_form()
        return context


class PhotoUploadView(generic.FormView):
    form_class = PersonForm
    template_name = 'administration/grade_detail.html'
    success_url = '/thanks/'


class GradeCreateView(views.SuperuserRequiredMixin, generic.CreateView):
    """
        Class to create a Grade object

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
        :return: The HttpResponse set in success_url
    """

    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'tests']

    def form_valid(self, form):
        grade = form.save(commit=False)
        grade.school_id = self.kwargs['pk']
        grade.save()

        return super(GradeCreateView, self).form_valid(form)


class GradeUpdateView(views.SuperuserRequiredMixin, generic.UpdateView):
    """
        Class to update a Grade object based on the id

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in
            as superuser
        :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
            saving the form when validated.
        :return: The HttpResponse set in success_url
    """
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'tests']




