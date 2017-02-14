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
from .forms import PersonForm, FileUpload, ChangePassword, SchoolForm

import datetime
from django.utils.safestring import mark_safe
import re

# Create your views here.


class AdministratorCheck:
    def test_func(self, user):
        if self.request.user.role == 4:
            return True
        return False



class SchoolCheck:
    def test_func(self, user):
        if self.request.user.role == 4:
            return True
        elif self.request.user.role == 3:
            school = School.objects.get(id=self.kwargs.get('pk'))
            if self.request.user.id == school.school_administrator.id or self.request.user.role == 4:
                return True
        elif self.request.user.role == 2:
            grades_teacher = Grade.objects.filter(person__username=self.request.user.username)
            grades = Grade.objects.filter(id=self.kwargs.get('pk'))
            for grade_teacher in grades_teacher:
                for grade in grades:
                    if grade_teacher == grade:
                        return True
        return False


class SchoolAdministratorCheck:
    def test_func(self, user):
        if self.request.user.role == 3 or self.request.user.role == 4:
            return True
        return False


class GradeCheck:
    def test_func(self, user):
        if self.request.user.role == 4:
            return True
        if self.request.user.role == 3 or self.request.user.role == 2:
            grades_teacher = Grade.objects.filter(person__username=self.request.user.username)
            print(grades_teacher)
            grades_student = Grade.objects.filter(person__username=self.kwargs.get('slug'))
            print(grades_student)
            for grade_teacher in grades_teacher:
                for grade_student in grades_student:
                    if grade_teacher == grade_student:
                        return True
        return False


class TeacherCheck:
    def test_func(self, user):
        if self.request.user.role == 2 or self.request.user.role == 3 or self.request.user.role == 4:
            return True
        return False

class MyPageDetailView(views.UserPassesTestMixin, generic.FormView):
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

    def get_context_data(self, **kwargs):
        context = super(MyPageDetailView, self).get_context_data(**kwargs)
        print(Person.objects.get(username=self.kwargs.get('slug')))
        context['person'] = Person.objects.get(username=self.kwargs.get('slug'))
        return context


class PersonListView(views.SuperuserRequiredMixin, views.AjaxResponseMixin, generic.ListView):
    """
        Class to list all the persons

        If the user is staff only students will show

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.ListView: Inherits generic.ListView that makes a page representing a list of objects.
        :return: List of person objects
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/person_list.html'
    model = Person


class PersonDisplayView(generic.DetailView):
    """
        Class to get a specific Person based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.DetailView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: Person object

    """

    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"

    def get_context_data(self, **kwargs):
        context = super(PersonDisplayView, self).get_context_data(**kwargs)
        context['form'] = ChangePassword()
        return context


class PersonDetailView(View):
    """
        View that shows information about a Person object based on the username

        :param gradecheck: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.DetailView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: Person object
    """

    def get(self, request, *args, **kwargs):
        """
        Redirects to the PersonDisplayView
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        view = PersonDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        redirects to ChangePasswordView
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        view = ChangePasswordView.as_view()
        return view(request, *args, **kwargs)


class ChangePasswordView(generic.FormView):
    """
        View that handles passwordchanging for a different user than the one that is logged in.
    """
    template_name = 'administration/person_detail.html'
    form_class = ChangePassword
    model = Person
    slug_field = 'username'

    def get_success_url(self):
        return reverse('administration:personDetail', kwargs={'slug': self.kwargs.get('slug')})

    def form_valid(self, form):
        pw = form.cleaned_data['password']
        pw2 = form.cleaned_data['password2']
        if pw == pw2:
            person = Person.objects.get(username=self.kwargs.get('slug'))
            person.set_password(pw)
            person.save()
        else:
            messages.error(self.request,'Feltene var ikke like')
        return super(ChangePasswordView, self).form_valid(form)


class PersonCreateView(SchoolCheck, views.UserPassesTestMixin,  generic.CreateView):
    """
        Class to create a Person object

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
    """

    login_url = reverse_lazy('login')
    role = 1
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
            print(self.kwargs.get('pk'))
            return {'grades': self.kwargs.get('pk'), 'role': self.role}

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


class PersonUpdateView(SchoolCheck, views.UserPassesTestMixin, generic.UpdateView):
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

    def get_context_data(self, **kwargs):
        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        context['schools'] = School.objects.all()
        context['gradesInfo'] = Grade.objects.all()
        return context


class SchoolListView(SchoolAdministratorCheck, views.UserPassesTestMixin, generic.ListView):
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

    def get_context_data(self, **kwargs):
        if self.request.user.role == 3:
            context = super(SchoolListView, self).get_context_data(**kwargs)
            context['object_list'] = School.objects.filter(school_administrator=self.request.user.id)
            return context
        return super(SchoolListView, self).get_context_data(**kwargs)



class SchoolDetailView(SchoolCheck, views.UserPassesTestMixin, generic.DetailView):
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
    form_class = SchoolForm
    success_url = reverse_lazy('administration:schoolList')




class SchoolUpdateView(SchoolCheck, views.UserPassesTestMixin, generic.UpdateView):
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


class GradeDisplay(generic.DetailView):
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
        context['persons'] = Person.objects.filter(grades__id=self.kwargs['pk'])
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
                p_date = re.match(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', str(person_obj[3]))
                if p_date:
                    person.date_of_birth = p_date.group(1)
                else:
                    person.date_of_birth = datetime.datetime.strptime(person_obj[3], "%d.%m.%Y").strftime("%Y-%m-%d")
                username = Person.createusername(person)
                person.username = username
                person.set_password('ntnu123')
                persons.append(person)
                line_number += 1
            except Exception:
                try:
                    datetime.datetime.strptime(person_obj[3], '%d.%m-%Y')
                    message = mark_safe('Noe gikk galt med ' + person_obj[0] + " " + person_obj[1] + ' på linje '+
                                   str(line_number) + "." + "<br /><br />" "Ingen brukere ble lagt til.")
                    messages.error(self.request, message)
                    return super().post(request, *args, **kwargs)
                except Exception:
                    message = mark_safe('Noe gikk galt med datoformatet. '
                                        'Fødselsdag må være på dd.mm.yyyy eller yyyy-mm-dd'
                                        "<br /><br />" "Ingen brukere ble lagt til.")
                    messages.error(self.request, message)
                    return super().post(request, *args, **kwargs)

        Person.objects.bulk_create(persons)
        grade = Grade.objects.get(id=self.kwargs.get('pk'))
        for person in persons:
            savedPerson = Person.objects.get(username=person.username)
            savedPerson.grades.add(grade)
        messages.success(self.request, str(len(persons)) + " elever ble lagt til!")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('administration:gradeDetail', kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'pk': self.kwargs.get('pk')})


class GradeDetailView(SchoolCheck, views.UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        view = GradeDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = FileUploadView.as_view()
        return view(request, *args, **kwargs)


class GradeCreateView(SchoolCheck, views.UserPassesTestMixin, generic.CreateView):
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



class GradeUpdateView(SchoolCheck, views.UserPassesTestMixin, generic.UpdateView):
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


class GradeListView(views.StaffuserRequiredMixin, generic.ListView):
    login_url = reverse_lazy('login')
    template_name = 'administration/gradeList.html'

    def get_queryset(self):
        return Grade.objects.filter(person__username=self.request.user.username)
