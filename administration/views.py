import datetime
import re
from braces import views
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views import View, generic

from .forms import (ChangePasswordForm, FileUploadForm, PersonForm,
                    SchoolAdministratorForm, SchoolForm)
from .models import Grade, Person, School, Gruppe
from maths.models import Test, TaskCollection

from django.db.models import Q
from django.http import Http404


class AdministratorCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has administrator privileges.

     **UserPassesTestMixin:**
        Mixin from :ref:`Django braces` that check is the logged in user passes the test given in :func:`test_func`.
    """

    def test_func(self, user):
        """
            :param user: Person that has to pass the test.
            :return: True if the user logged in as an administrator.
        """
        if user.is_authenticated():
            if user.role == 4:
                return True
        return False


class RoleCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user is either a teacher, school administrator or an administrator.

     **UserPassesTestMixin:**
        Mixin from :ref:`Django braces` that check is the logged in user passes the test given in :func:`test_func`
    """

    def test_func(self, user):
        """
            :param user: Person that has to pass the test.
            :return: True if the user is an administrator, school administrator or a teacher.
        """
        role = [2, 3, 4]
        if user.is_authenticated():
            if user.role in role:
                return True
        return False


class SchoolCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has sufficient access privileges to view or alter an object.

    **UserPassesTestMixin:**
        Mixin from :ref:`Django braces` that check is the logged in user passes the test given in :func:`test_func`

    """

    def test_func(self, user):
        """
            :param user: Person that has to pass the test.
            :return: True if the user is an administrator, school-administrator or is a teacher in one of the grades
                the relevant person object is in.
        """
        if user.is_authenticated():
            if user.role == 4:
                return True
            elif user.role == 3:
                if self.request.is_ajax():
                    return True
                if self.kwargs.get('school_pk'):
                    school = School.objects.get(id=self.kwargs.get('school_pk'))
                    if user.id == school.school_administrator.id:
                        return True
                if self.kwargs.get('slug'):
                    schools = School.objects.filter(school_administrator=user.id)
                    persons = Person.objects.filter(grades__school_id__in=schools)
                    for person in persons:
                        if person.username == self.kwargs.get('slug'):
                            return True
            elif user.role == 2:
                if self.kwargs.get('grade_pk'):
                    grades_teacher = Grade.objects.filter(person__username=self.request.user.username)
                    grades = Grade.objects.filter(id=self.kwargs.get('grade_pk'))
                    for grade_teacher in grades_teacher:
                        for grade in grades:
                            if grade_teacher == grade:
                                return True
                elif self.kwargs.get('slug'):
                    grades = user.grades.all()
                    persons = Person.objects.filter(grades__in=grades).distinct()
                    for person in persons:
                        if person.username == self.kwargs.get('slug'):
                            return True
            if self.kwargs.get('slug'):
                school_admin = School.objects.filter(school_administrator__username__exact=self.kwargs.get('slug'))
                if school_admin:
                    return True
                if self.kwargs.get('slug') == user.username:
                    return True
        return False


class SchoolAdministratorCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user is an administrator or school administrator.

    **UserPassesTestMixin:**
        Mixin from :ref:`Django braces` that check is the logged in user passes the test given in :func:`test_func`

    """

    def test_func(self, user):
        """
        :param user: Person that has to pass the test.
        :return: True if user is either a school administrator or administrator
        """
        if user.is_authenticated():
            if user.role == 3 or user.role == 4:
                return True
        return False


class MyPageDetailView(views.UserPassesTestMixin, views.AjaxResponseMixin, generic.FormView):
    """
    View that shows a user information about itself and allows them to change their password.


    **UserPassesTestMixin :**
        Mixin from :ref:`Django braces`
        Checks if the logged in user passes a given test. The test is given in :func:`test_func`.
    **FormView :**
        A view that displays a form

    :return: Own Person object and PasswordChangeForm
    """

    form_class = PasswordChangeForm
    slug_field = 'username'
    template_name = 'administration/mypage.html'

    def post_ajax(self, request, *args, **kwargs):
        new_email = request.POST['newEmail']
        username = request.POST['username']
        person = Person.objects.get(username=username)
        person.email = new_email
        person.save()
        data = {
            'new_email': person.email
        }
        return JsonResponse(data)

    def get_ajax(self, request, *args, **kwargs):
        students = []
        teachers = []
        grade_id = request.GET['grade_id']
        student_list = Person.objects.filter(role=1, grades__id=grade_id)
        teacher_list = Person.objects.filter(role=2, grades__id=grade_id)
        for student in student_list:
            students.append({
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email
            })
        for teacher in teacher_list:
            teachers.append({
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
                "email": teacher.email
            })
        data = {
            'students': students,
            'teachers': teachers
        }
        return JsonResponse(data)

    def test_func(self, user):
        """
        Checks if the logged in user is the same as the requested

        :param user: The logged in user
        :return: True or false depending on the user
        """
        return user.username == self.kwargs.get('slug')

    def get_success_url(self):
        """
        Determine the URL to redirect to when the form is successfully validated.

        :return: The Success url
        """
        return reverse('administration:myPage', kwargs={'slug': self.kwargs.get('slug')})

    def get_form(self, form_class=form_class):
        """
        Instantiate an instance of form_class using get_form_kwargs() that build the keyword arguments required to
        instantiate the form.

        :param form_class: The form class to instantiate. In this case Django's PasswordChageForm
        :return: The instantiated form
        """
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """
        Checks if the form that has been posted is valid

        :param form: The filled out PasswordChangeForm
        :return: The validated form
        """
        person = form.save(commit=False)
        password = form.cleaned_data['new_password1']
        person.set_password(password)
        person.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Passordet ble oppdatert!')
        return super(MyPageDetailView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Function that adds a person object to the context without overriding it.

        :param kwargs: Keyword arguments
        :return: Returns the updated context
        """
        context = super(MyPageDetailView, self).get_context_data(**kwargs)
        context['person'] = Person.objects.get(username=self.kwargs.get('slug'))
        if self.request.user.role == 1:
            context['groups'] = Gruppe.objects.filter(is_active=1, visible=True,
                                                      persons__username=self.request.user.username)
        elif self.request.user.role == 4:
            context['groups'] = Gruppe.objects.filter(is_active=1, creator=self.request.user)
            context['tests'] = TaskCollection.objects.filter(author=self.request.user)
        return context


class PersonListView(RoleCheck, views.AjaxResponseMixin, generic.ListView):
    """
    Class that returns all the users that the logged in user has permission to see.

    :func:`RoleCheck`:
        Permission check, only allows teachers, administrators and school administrators.
    **AjaxResponseMixin**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **ListView:**
        Inherits generic.ListView that makes a page representing a list of objects.

    :return: List of Person objects
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/person_list.html'
    model = Person

    def get_ajax(self, request, *args, **kwargs):
        """
        Function that checks if the get request is an ajax request and returns the persons matching the school or the
        grade.

        :param request: Request that was sent to PersonListView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: JsonResponse containing the necessary Person information
        """
        persons = []
        if request.GET['type'] == "school":
            school_id = request.GET['school_id']
            existing_person_list = Person.objects.filter(grades__school_id=school_id).distinct()
        else:
            grade_id = request.GET['grade_id']
            existing_person_list = Person.objects.filter(grades__id=grade_id).distinct()
        for person in existing_person_list.all():
            persons.append({
                "id": person.id,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "username": person.username,
                "role": person.role
            })
        data = {
            'persons': persons,
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Overrides the the original :func:`~administration.PersonListView.get_context_data` function and alters the
        person list so it fits with the permissions

        :param kwargs: Keyword arguments
        :return: The updated context data
        """
        context = super(PersonListView, self).get_context_data(**kwargs)
        if self.request.user.role == 4:
            context['schools'] = School.objects.all()
            context['grades'] = Grade.objects.all()
        elif self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            persons = Person.objects.filter(grades__school_id__in=schools).distinct()
            context['object_list'] = persons
            context['schools'] = schools
            grades = Grade.objects.filter(school__in=schools)
            context['grades'] = grades
        elif self.request.user.role == 2:
            grades = self.request.user.grades.all()
            persons = Person.objects.filter(grades__in=grades).distinct()
            context['object_list'] = persons
            context['grades'] = grades
        return context


class PersonDisplayView(views.AjaxResponseMixin, generic.DetailView):
    """
    Class to get a specific Person object based on the username.

    **DetailView:**
        Inherits Django's DetailView displaying a single Person Object
    :return: Person object

    """
    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"

    def get_ajax(self, request, *args, **kwargs):
        username = self.kwargs.get('slug')
        person = Person.objects.get(username=username)
        grades = []
        for grade in person.grades.all():
            grades.append({
                'grade': grade.grade_name + " - " + grade.school.school_name
            })
        data = {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'date_of_birth': person.date_of_birth,
            'sex': person.sex,
            'grades': grades,
            'last_login': person.last_login,
            'email': person.email,
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Function that adds a form to the context without overriding it.

        :param kwargs: keyword-arguments
        :return: The updated context
        """
        context = super(PersonDisplayView, self).get_context_data(**kwargs)
        username = self.kwargs.get('slug')
        person = Person.objects.get(username=username)
        if person.role == 1:
            tests = Test.objects.filter(
                Q(person=person) | Q(grade__in=person.grades.all()) | Q(gruppe__in=person.gruppe_set.all())).distinct()
            print(tests)
            context['tests'] = tests
            print(context['tests'])
        elif person.role == 2:
            tests = Test.objects.filter(person=person)
            context['tests'] = tests
        if self.kwargs.get('grade_pk'):
            context['grade_pk'] = self.kwargs['grade_pk']
            context['school_pk'] = self.kwargs['school_pk']
        groups = Gruppe.objects.filter(is_active=1, persons__username=self.kwargs['slug'])
        groups_creator = Gruppe.objects.filter(is_active=1, creator__username=self.kwargs['slug'])
        if groups:
            context['groups'] = groups
        if groups_creator:
            context['groups'] = groups_creator
        context['form'] = ChangePasswordForm()
        return context


class PersonDetailView(SchoolCheck, View):
    """
    View that handles PersonDisplayView (HTTP GET) and the ChangePasswordView (HTTP POST), this view is not displayed

    :func:`SchoolCheck`:
        Permission check
    **View**
        Intentionally simple parent class for all views.
    """

    def get(self, request, *args, **kwargs):
        """
        Takes all HTTP GET methods and redirects it to the :func:`PersonDisplayView`

        :param request: request that was sent to PersonDetaiLView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the PersonDisplayView with the same parameters that this method got
        """
        view = PersonDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Takes all HTTP POST methods and redirects it to the :func:`ChangePasswordView`

        :param request: Request that was sent to PersonDetaiLView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: The ChangePasswordView with the same parameters that this method got
        """
        view = ChangePasswordView.as_view()
        return view(request, *args, **kwargs)


class ChangePasswordView(generic.FormView):
    """
    View that handles changing password for a different user than the one that is logged in.

    **FormView**
        A view that displays a form
    """
    template_name = 'administration/person_detail.html'
    form_class = ChangePasswordForm
    model = Person
    slug_field = 'username'

    def get_success_url(self):
        """
        Determines the URL to redirect to when the form is successfully validated.

        :return: The Success url
        """
        return reverse('administration:personDetail', kwargs={'slug': self.kwargs.get('slug')})

    def form_valid(self, form):
        """
        Function that checks if the submitted text is correct, and if correct sets this as the new password of the user.
        If the passwords don't match it returns an error message.

        :param form: References to the filled out model form.
        :return: calls super with the new form
        """
        pw = form.cleaned_data['password']
        pw2 = form.cleaned_data['password2']
        if pw == pw2:
            person = Person.objects.get(username=self.kwargs.get('slug'))
            person.set_password(pw)
            person.save()
            messages.success(self.request, 'Passordet ble oppdatert!')
        else:
            messages.error(self.request, 'Feltene var ikke like. Passordet ble ikke oppdatert')
        return super(ChangePasswordView, self).form_valid(form)


class PersonCreateView(RoleCheck, generic.CreateView):
    """
    Creates a Person object

    :func:`RoleCheck`:
        Permission check, only allows teachers, administrators and school administrators.
    **CreateView:**
        get
    """

    login_url = reverse_lazy('login')
    role = 1
    template_name = 'administration/person_form.html'
    form_class = PersonForm
    success_url = reverse_lazy('administration:personList')

    def get_initial(self):
        """
        Function that checks for preset Person values and sets them to the fields

        :return: List of the preset values
        """

        if self.kwargs.get('grade_pk'):
            self.success_url = reverse_lazy('administration:gradeDetail',
                                            kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'grade_pk': self.kwargs.get('grade_pk')})
            initial = super(PersonCreateView, self).get_initial()
            initial['grades'] = [self.kwargs.get('grade_pk')]
            initial['role'] = self.role
            return initial

    def form_valid(self, form):
        """
        Function that overrides form_valid and saves a new person object to the database.

        :param form: References to the model form.
        :return: Validated form
        """

        person = form.save(commit=False)
        if self.request.user.role == 3:
            if person.role > 3 or person.role < 1:
                return super(PersonCreateView, self).form_invalid(form)
        elif self.request.user.role == 2:
            if person.role != 1:
                return super(PersonCreateView, self).form_invalid(form)
        if person.role == 4:
            person.is_staff = True
            person.is_superuser = True
        elif person.role == 3 or person.role == 2:
            person.is_staff = True
        username = Person.create_username(person)
        person.username = username
        person.set_password('ntnu123')
        person.save()
        messages.success(self.request, person.get_full_name() + " ble opprettet med brukernavnet: " + person.username)
        return super(PersonCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Function that adds data to the context without overriding it, adds different data depending on the
        logged in users role.

        :param kwargs: Keyword-arguments
        :return: returns the updated context
        """
        context = super(PersonCreateView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            context['schools'] = schools
            context['gradesInfo'] = Grade.objects.filter(school_id__in=schools)
        elif self.request.user.role == 2:
            grades = self.request.user.grades.all()
            school_ids = []
            for grade in grades:
                school_ids.append(grade.school_id)
            schools = School.objects.filter(id__in=school_ids).distinct()
            context['schools'] = schools
            context['gradesInfo'] = grades
        else:
            context['schools'] = School.objects.all()
            context['gradesInfo'] = Grade.objects.all()
        if self.kwargs.get('grade_pk'):
            context['fromGrade'] = Grade.objects.get(id=self.kwargs.get('grade_pk'))
        return context


class PersonUpdateView(SchoolCheck, views.AjaxResponseMixin, generic.UpdateView):
    """
    Class that updates a Person object

    :func:`SchoolCheck`:
        Permission check.
    **AjaxResponseMixin**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """

    template_name = 'administration/person_form.html'
    login_url = reverse_lazy('login')
    form_class = PersonForm
    model = Person
    my_page = False
    slug_field = "username"

    def get_success_url(self):
        if self.request.user.username == self.kwargs.get('slug'):
            url = reverse_lazy('administration:myPage', kwargs={'slug': self.kwargs.get('slug')})
        else:
            url = super(PersonUpdateView, self).get_success_url()
        return url

    def form_valid(self, form):
        """
            Function that validates and saves the updated Person object.

            :param form: References to the model form.
            :return: Validated form
        """
        person = form.save(commit=False)
        if self.kwargs.get('slug') != self.request.user.username:
            if self.request.user.role == 3:
                if person.role > 3 or person.role < 1:
                    return super(PersonUpdateView, self).form_invalid(form)
            elif self.request.user.role == 2:
                if person.role != 1:
                    return super(PersonUpdateView, self).form_invalid(form)
        person.save()
        return super(PersonUpdateView, self).form_valid(form)

    def post_ajax(self, request, *args, **kwargs):
        """
        Function that checks if the post request is an ajax post and adds the selected grade to the Person.

        :param request: Request that was sent to PersonUpdateView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: JsonResponse containing the necessary Person information
        """
        grade = Grade.objects.get(id=request.POST['grade'])
        person = self.get_object()
        person.grades.add(grade)
        person.save()
        data = {
            'username': person.username,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'role': person.role,
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Function that adds data to the context without overriding it, adds different data depending on the logged in
        users role.

        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            context['schools'] = schools
            context['gradesInfo'] = Grade.objects.filter(school_id__in=schools)
        elif self.request.user.role == 2:
            grades = self.request.user.grades.all()
            school_ids = []
            for grade in grades:
                school_ids.append(grade.school_id)
            schools = School.objects.filter(id__in=school_ids).distinct()
            context['schools'] = schools
            context['gradesInfo'] = grades
        else:
            context['schools'] = School.objects.all()
            context['gradesInfo'] = Grade.objects.all()
        if self.kwargs.get('grade_pk'):
            context['fromGrade'] = Grade.objects.get(id=self.kwargs.get('grade_pk'))
        return context


class PersonDeleteView(SchoolAdministratorCheck, generic.DeleteView):
    """
    Class that updates a Person object

    :func:`SchoolCheck`:
        Permission check.
    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    slug_field = 'username'
    model = Person

    def get_object(self, queryset=None):
        obj = super(PersonDeleteView, self).get_object()
        if not obj.last_login:
            return obj
        raise Http404

    def get_success_url(self):
        success_url = reverse_lazy('administration:personList')
        print(self.kwargs.get('grade_pk'))
        if self.kwargs.get('grade_pk'):
            print()
            success_url = reverse_lazy('administration:gradeDetail',
                                       kwargs={'school_pk': self.kwargs.get('school_pk'),
                                               'grade_pk': self.kwargs.get('grade_pk')})
        return success_url

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SchoolListView(SchoolAdministratorCheck, generic.ListView):
    """
    Class to list out all School objects

    :func:`SchoolAdministratorCheck`:
        Permission check
    **ListView:**
        Inherits Django's ListView that represents a page containing a list of objects
    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_list.html'

    def get_context_data(self, **kwargs):
        """
        Function that adds data to the context without overriding it, adds different data depending on the logged in
        users role.

        :param kwargs: Keyword-arguments
        :return: The updated context
        """
        if self.request.user.role == 3:
            context = super(SchoolListView, self).get_context_data(**kwargs)
            context['object_list'] = School.objects.filter(school_administrator=self.request.user.id)
            return context
        return super(SchoolListView, self).get_context_data(**kwargs)


class SchoolDetailView(SchoolCheck, generic.DetailView):
    """
    Class that displays information about a specific school based on the school_id.

    :func:`SchoolCheck`:
        Inherited permission check
    **DetailView**
        Inherits Django's DetailView displaying a single School Object
    """
    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_detail.html'
    pk_url_kwarg = 'school_pk'

    def get_context_data(self, **kwargs):
        """
        Function that adds the schools grade objects to the context without overriding it.

        :param kwargs: Keyword-arguments
        :return: The updated context
        """
        context = super(SchoolDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.filter(school_id=self.kwargs['school_pk'])
        return context


class SchoolCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    """
    Class to create a School object

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **AjaxResponseMixin**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **CreateView:**
        Inherits generic.CreateView that displays a form for creating a object and
        saving the form when validated
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/school_form.html'
    form_class = SchoolForm
    success_url = reverse_lazy('administration:schoolList')

    def post_ajax(self, request, *args, **kwargs):
        """
        Function that checks if the post request is an ajax post and creates a new school administrator.

        :param request: Request that was sent to PersonUpdateView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: JsonResponse with the necessary Person information.
        """
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        date_of_birth = request.POST['date_of_birth']
        sex = request.POST['sex']
        person = Person(first_name=first_name, last_name=last_name, email=email, sex=sex)
        try:
            person.date_of_birth = datetime.datetime.strptime(date_of_birth, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            data = {
                'message': 'Ikke rett format på fødselsdato. Må være på formen dd.mm.yyyy'
            }
            return JsonResponse(data)
        username = person.create_username()
        person.username = username
        person.role = 3
        person.set_password('ntnu123')
        person.save()
        data = {
            'username': person.username,
            'id': person.id,
            'first_name': person.first_name,
            'last_name': person.last_name
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Function that adds the SchoolAdministrator form to the context without overriding it.

        :param kwargs: Keyword-arguments
        :return: The updated context
        """
        context = super(SchoolCreateView, self).get_context_data(**kwargs)
        context['administratorForm'] = SchoolAdministratorForm()
        return context

    def form_valid(self, form):
        """
        Overrides generic.CreateViews form_valid and adds a success message to the request.
        :param form: represents the form object
        :return: calls super
        """
        school = form.save()
        messages.success(self.request, 'Skole med navnet: ' + school.school_name + " ble opprettet!")
        return super(SchoolCreateView, self).form_valid(form)


class SchoolUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update information about a school object based on the school_id.

    :func:`SchoolCheck`:
        Permission check
    **UpdateView:**
        Inherits Django's Update that displays a form for updating a specific object and
        saving the form when validated.
    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_form.html'
    form_class = SchoolForm
    pk_url_kwarg = 'school_pk'

    def get_context_data(self, **kwargs):
        """
        Function that adds the SchoolAdministrator form to the context without overriding it.

        :param kwargs: Keyword-arguments
        :return: The updated context
        """
        context = super(SchoolUpdateView, self).get_context_data(**kwargs)
        context['administratorForm'] = SchoolAdministratorForm()
        return context


class GradeListView(RoleCheck, generic.ListView):
    """
    Class that displays a list of grade objects

    :func:`RoleCheck`:
        Permission check, only allows teachers, administrators and school administrators.
    **ListView**
        Inherits Django's ListView that represents a page containing a list of objects.
    """
    login_url = reverse_lazy('login')
    template_name = 'administration/gradeList.html'

    def get_queryset(self):
        """
        Function that defines the queryset.

        :return: List of grades.
        """
        return Grade.objects.filter(person__username=self.request.user.username)


class GradeDisplay(views.AjaxResponseMixin, generic.DetailView):
    """
    Class that displays information about a single grade object based on the grade_id

    **DetailView:**
        Inherits generic.DetailView that makes a page representing a specific object.
    """
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_detail.html'
    pk_url_kwarg = 'grade_pk'

    def get_context_data(self, **kwargs):
        """
        Function that adds objects and a FileUpload form to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(GradeDisplay, self).get_context_data(**kwargs)
        context['persons'] = Person.objects.filter(grades__id=self.kwargs['grade_pk'])
        context['schools'] = School.objects.all()
        context['grades'] = Grade.objects.all().exclude(id=self.kwargs['grade_pk'])
        context['groups'] = Gruppe.objects.filter(grade__id=self.kwargs['grade_pk'])
        context['existingStudents'] = Person.objects.filter(role=1, is_active=1).exclude(
            grades__id=self.kwargs['grade_pk'])
        context['existingTeachers'] = Person.objects.filter(role=2, is_active=1).exclude(
            grades__id=self.kwargs['grade_pk'])
        context['form'] = FileUploadForm()
        return context


class FileUploadView(generic.FormView):
    """
    Class that handles uploading excel files using :ref:`Django-excel` and creates Person objects from them.
    
     **FormView**
        A view that displays a form.
    """

    template_name = 'administration/grade_detail.html'
    form_class = FileUploadForm
    model = Person

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST methods and creates Person objects from the given Excel file.

        :param request: Request that was sent to PersonUpdateView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: 
        """
        persons = []
        order = ['fornavn', 'etternavn', 'epost', 'fødselsdag', 'kjønn']
        try:
            person_dict = request.FILES['file'].get_array()
        except Exception:
            message = mark_safe('Dette filformatet er ikke støttet.')
            messages.error(self.request, message)
            return super().post(request, *args, **kwargs)
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
                username = Person.create_username(person)
                person.username = username
                person.set_password('ntnu123')
                personCheck = Person.objects.filter(first_name=person.first_name, last_name=person.last_name,
                                                    date_of_birth=person.date_of_birth)
                if not personCheck:
                    persons.append(person)
                    line_number += 1
                else:
                    message = person.first_name + " " + person.last_name + " med fødselsdag " + person.date_of_birth + \
                              " ble ikke lagt til for at en person med samme detaljer allerede er registrert."
                    messages.error(self.request, message)
            except Exception:
                try:
                    datetime.datetime.strptime(person_obj[3], '%d.%m-%Y')
                    message = mark_safe('Noe gikk galt med ' + person_obj[0] + " " + person_obj[1] + ' på linje ' +
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
        grade = Grade.objects.get(id=self.kwargs.get('grade_pk'))
        for person in persons:
            savedPerson = Person.objects.get(username=person.username)
            savedPerson.grades.add(grade)
        messages.success(self.request, str(len(persons)) + " elever ble lagt til!")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determines the URL to redirect to when the Post is successful.

        :return: The Success url
        """
        return reverse('administration:gradeDetail', kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                             'grade_pk': self.kwargs.get('grade_pk')})


class GradeDetailView(SchoolCheck, View):
    """
    View that handles GradeDisplay and the FileUploadView, this view is not displayed

    :func:`SchoolCheck`:
        Permission check
    """

    def get(self, request, *args, **kwargs):
        """
        Handels all get requests and redirects to :func:`GradeDisplay`

        :param request: request that was sent to GradeDetailView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the GradeDisplay with the same parameters that this method got
        """
        view = GradeDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles all post request and redirects to the :func:`FileUploadView`

        :param request: request that was sent to FileUploadView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the FileUploadView with the same parameters that this method got
        """
        view = FileUploadView.as_view()
        return view(request, *args, **kwargs)


class GradeCreateView(SchoolCheck, generic.CreateView):
    """
    Class to create a Grade object

    :func:`SchoolCheck`:
        Inherited permission check
    **CreateView:**
        Inherits generic.CreateView that displays a form for creating a object and
        saving the form when validated
    """

    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'is_active']

    def form_valid(self, form):
        """
        Overrides generic.CreateViews form_valid and saves a grade to a specific school
        :param form: represents the form object
        :return: calls super
        """
        self.success_url = reverse_lazy('administration:schoolDetail',
                                        kwargs={'school_pk': self.kwargs.get('school_pk')})
        grade = form.save(commit=False)
        grade.school_id = self.kwargs['school_pk']
        grade.save()
        messages.success(self.request, 'Klasse med navnet: ' + grade.grade_name + " ble opprettet.")
        return super(GradeCreateView, self).form_valid(form)


class GradeUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update a Grade object

    :func:`SchoolCheck`:
        Inherited permission check
    **UpdateView:**
        Inherits generic.UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    pk_url_kwarg = 'grade_pk'
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'is_active']

    def get_success_url(self):
        """
        Determines the URL to redirect to when the Post is successful.

        :return: The Success url
        """
        return reverse_lazy('administration:gradeDetail', kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                                  'grade_pk': self.kwargs.get('grade_pk')})


class GroupListView(AdministratorCheck, generic.ListView):
    """
    Class that displays a list of group objects.

    :func:`AdministratorCheck`:
        Inherited permission check
    **ListView:**
        Inherits Django's ListView that represents a page containing a list of objects.
    """
    template_name = 'administration/group_list.html'
    model = Gruppe


class GroupDetailView(views.AjaxResponseMixin, generic.DetailView):
    """
    Class that displays information about a single grade object based on the grade_id

    :func:`AdministratorCheck`:
        Inherited permission check
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **DetailView:**
        Inherits generic.DetailView that makes a page representing a specific object.
    """
    template_name = 'administration/group_detail.html'
    model = Gruppe
    pk_url_kwarg = 'group_pk'

    def get_ajax(self, request, *args, **kwargs):
        """
        Function that checks if the get request is an ajax request and returns the persons in the group.

        :param request: Request that was sent to GroupDetailView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: JsonResponse containing the necessary Person information
        """
        persons = []
        person_list = Person.objects.filter(gruppe__id=self.kwargs.get('group_pk'))
        for person in person_list:
            persons.append({
                "first_name": person.first_name,
                "last_name": person.last_name,
                "username": person.username,
                "email": person.email
            })
        data = {
            'persons': persons
        }
        return JsonResponse(data)


class GroupCreateView(SchoolAdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    """
    Class that displays information about a single grade object based on the grade_id

    :func:`AdministratorCheck`:
        Inherited permission check
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **CreateView:**
        Inherits generic.CreateView that displays a form for creating a object and
        saving the form when validated
    """
    model = Gruppe
    fields = ['group_name', 'persons', 'is_active', 'visible', 'grade']
    template_name = 'administration/group_form.html'
    success_url = reverse_lazy('administration:groupList')

    def get_initial(self):
        """
        Function that checks for preset values and sets them to the fields.

        :return: List of the preset values.
        """
        if self.kwargs.get('grade_pk'):
            self.success_url = reverse_lazy('administration:gradeDetail',
                                            kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'grade_pk': self.kwargs.get('grade_pk')})
            return {'grade': self.kwargs.get('grade_pk')}

    def get_ajax(self, request, *args, **kwargs):
        """
        Function that checks if the get request is an ajax request and returns the persons matching the role and
        school/grade.

        :param request: Request that was sent to GroupCreateView
        :param args:  Arguments that were sent with the request
        :param kwargs: Keyword-arguments
        :return: JsonResponse containing the necessary Person information
        """
        role = request.GET['role']
        persons = []
        if request.GET['type'] == "school":
            school_id = request.GET['school_id']
            existing_person_list = Person.objects.filter(grades__school_id=school_id, role=role).distinct()
        else:
            grade_id = request.GET['grade_id']
            existing_person_list = Person.objects.filter(grades__id=grade_id, role=role).distinct()
        for person in existing_person_list.all():
            persons.append({
                "id": person.id,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "username": person.username,
                "role": person.role
            })
        data = {
            'persons': persons,
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Function that adds objects to the context without overriding it.
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(GroupCreateView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            context['schools'] = School.objects.filter(school_administrator=self.request.user)
            context['grades'] = Grade.objects.filter(school__school_administrator=self.request.user)
            context['students'] = Person.objects.filter(grades__school__school_administrator=self.request.user, role=1)
        else:
            context['schools'] = School.objects.all()
            context['grades'] = Grade.objects.all()
            context['students'] = Person.objects.filter(role=1)
        return context

    def form_valid(self, form):
        """
        Overrides generic.CreateViews form_valid and adds the creator to the group and then saves it.
        :param form: represents the form object
        :return: calls super
        """
        gruppe = form.save(commit=False)
        gruppe.creator_id = self.request.user.id
        gruppe.save()
        messages.success(self.request, 'Gruppe med navnet: ' + gruppe.group_name + " ble opprettet.")
        return super(GroupCreateView, self).form_valid(form)


class GroupUpdateView(SchoolAdministratorCheck, generic.UpdateView):
    """
    Class to update a specific group object bases on the group_id

    :func:`AdministratorCheck`:
        Inherited permission check
    **UpdateView:**
        Inherits generic.UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    model = Gruppe
    template_name = 'administration/group_form.html'
    fields = ['group_name', 'is_active', 'persons', 'visible', 'grade']
    pk_url_kwarg = 'group_pk'

    def get_success_url(self):
        """
        Determines the URL to redirect to when the Post is successful.

        :return: The Success url
        """
        return reverse_lazy('administration:groupDetail', kwargs={'group_pk': self.kwargs.get('group_pk')})

    def get_context_data(self, **kwargs):
        """
        Function that adds objects to the context without overriding it.
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(GroupUpdateView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            context['schools'] = School.objects.filter(school_administrator=self.request.user)
            context['grades'] = Grade.objects.filter(school__school_administrator=self.request.user)
            context['students'] = Person.objects.filter(grades__school__school_administrator=self.request.user, role=1)
        else:
            context['schools'] = School.objects.all()
            context['grades'] = Grade.objects.all()
            context['students'] = Person.objects.filter(role=1)
        return context
