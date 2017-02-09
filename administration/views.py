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
from django.views import View

import logging
from django.core import serializers
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from .forms import PersonForm, FileUpload

import datetime
from django.utils.safestring import mark_safe


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
        person = form.save(commit=False)
        username = Person.createusername(person)
        person.username = username
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


class GradeDisplay(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Grade based on the grade.id

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.UpdateView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: School object
    """
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_detail.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(GradeDisplay, self).get_context_data(**kwargs)
        context['students'] = Person.objects.filter(grades__id=self.kwargs['pk'], is_staff=False)
        context['teachers'] = Person.objects.filter(grades__id=self.kwargs['pk'], is_staff=True)
        context['form'] = FileUpload()
        return context


class FileUploadView(generic.FormView):
    template_name = 'administration/grade_detail.html'
    form_class = FileUpload
    model = Person

    def post(self, request, *args, **kwargs):
        persons = []
        order = ['fornavn', 'etternavn', 'epost', 'fødselsdag', 'kjønn']
        person_dict = request.FILES['file'].get_array()
        line_number = 2
        for person_obj in person_dict[:1]:
            for field, correct_field in zip(person_obj, order):
                print(field, correct_field)
                if not str(field).lower() == str(correct_field).lower():
                    message = mark_safe('Feltene dine samsvarer ikke med de påkrevde.'
                                        "<br /><br />"
                                        'Fornavn - Etternavn - Epost - Fødselsdag - Kjønn')
                    messages.error(self.request, message)
                    return super().post(request, *args, **kwargs)
        for person_obj in person_dict[1:]:
            try:
                person = Person(first_name=person_obj[0], last_name=person_obj[1],
                                email=person_obj[2], sex=person_obj[4])
                person.date_of_birth = datetime.datetime.strptime(person_obj[3], "%d.%m.%Y").strftime("%Y-%m-%d")
                username = Person.createusername(person)
                person.username = username
                person.set_password('ntnu123')
                person.grade_id = self.kwargs.get('pk')
                persons.append(person)
                line_number += 1
            except Exception:
                message = mark_safe('Noe gikk galt med ' + person_obj[0] + " " + person_obj[1] + ' på linje '+
                               str(line_number) + "." + "<br /><br />" "Ingen brukere ble lagt til.")
                messages.error(self.request, message)
                return super().post(request, *args, **kwargs)
        Person.objects.bulk_create(persons)
        messages.success(self.request, str(len(persons)) + " elever ble lagt til!")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('administration:gradeDetail', kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'pk': self.kwargs.get('pk')})


class GradeDetailView(View):
    def get(self, request, *args, **kwargs):
        view = GradeDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = FileUploadView.as_view()
        return view(request, *args, **kwargs)


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
        self.success_url = reverse_lazy('administration:schoolDetail', kwargs={'pk': self.kwargs.get('pk')})
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




