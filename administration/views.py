import datetime
import re
from django.core import serializers
from braces import views
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse, reverse_lazy
# Create your views here.
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views import View, generic

from .forms import (ChangePassword, FileUpload, PersonForm,
                    SchoolAdministrator, SchoolForm)
from .models import Grade, Person, School, Gruppe


class AdministratorCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has administrator privileges.
    """

    def test_func(self, user):
        if self.request.user.is_authenticated():
            if self.request.user.role == 4:
                return True
        return False


class RoleCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user is either a teacher, schooladministrator or an administrator.
    """

    def test_func(self, user):
        role = [2, 3, 4]
        if self.request.user.is_authenticated():
            if self.request.user.role in role:
                return True
        return False


class SchoolCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has sufficient access privileges to view a object.
    :param views.UserPassesTestMixin: djangos way of handling restricted access, it's test_func is overriden.
    :return boolean, True if access is granted.
    """

    def test_func(self, user):
        """
        :param user: Test_func has to have two arguments.
        :return: returns true if the user is administrator, school-administrator or is a teacher in one of the grades
        the relevant person object is in
        """
        if self.request.user.is_authenticated():
            if self.request.user.role == 4:
                return True
            elif self.request.user.role == 3:
                if self.kwargs.get('school_pk'):
                    school = School.objects.get(id=self.kwargs.get('school_pk'))
                    if self.request.user.id == school.school_administrator.id:
                        return True
                if self.kwargs.get('slug'):
                    schools = School.objects.filter(school_administrator=self.request.user.id)
                    persons = Person.objects.filter(grades__school_id__in=schools)
                    for person in persons:
                        if person.username == self.kwargs.get('slug'):
                            return True
            elif self.request.user.role == 2:
                if self.kwargs.get('grade_pk'):
                    grades_teacher = Grade.objects.filter(person__username=self.request.user.username)
                    grades = Grade.objects.filter(id=self.kwargs.get('grade_pk'))
                    for grade_teacher in grades_teacher:
                        for grade in grades:
                            if grade_teacher == grade:
                                return True
                elif self.kwargs.get('slug'):
                    grades = self.request.user.grades.all()
                    persons = Person.objects.filter(grades__in=grades).distinct()
                    for person in persons:
                        if person.username == self.kwargs.get('slug'):
                            return True
            if self.kwargs.get('slug'):
                school_admin = School.objects.filter(school_administrator__username__exact=self.kwargs.get('slug'))
                if school_admin:
                    return True
        return False


class SchoolAdministratorCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user is school-administrator or administrator
    :param views.UserPassesTestMixin: djangos way of handling restricted access, it's test_func is overriden.
    :return boolean, True if access is granted.
    """

    def test_func(self, user):
        """

        :param user: Test_func has to have two arguments.
        :return: returns true if user is either school_administrator or administrator
        """
        if self.request.user.is_authenticated():
            if self.request.user.role == 3 or self.request.user.role == 4:
                return True
        return False


class MyPageDetailView(views.UserPassesTestMixin, generic.FormView):
    """
    View that shows a user information about itself and allows them to change their password.


    **UserPassesTestMixin :**
        Checks if the logged in user passes a given test. The test is given in **test_func**.
    **FormView :**
        A view that displays a form


    :return: Own Person object and PasswordChangeForm
    """

    form_class = PasswordChangeForm
    slug_field = 'username'
    template_name = 'administration/mypage.html'

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
        return context


class PersonListView(RoleCheck, views.AjaxResponseMixin, generic.ListView):
    """
    Class that returns all the users that the logged in user has permission to see.

    **RoleCheck:**
        Permission check, only allows teachers, administrators and school administrators.
    **ListView:**
        Inherits generic.ListView that makes a page representing a list of objects.

    :return: List of Person objects
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/person_list.html'
    model = Person

    def get_ajax(self, request, *args, **kwargs):
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
        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            persons = Person.objects.filter(grades__school_id__in=schools).distinct()
            context['object_list'] = persons
            context['schools'] = schools
            grades = Grade.objects.filter(school__exact=schools)
            context['grades'] = grades
            return context
        if self.request.user.role == 2:
            grades = self.request.user.grades.all()
            persons = Person.objects.filter(grades__in=grades).distinct()
            context['object_list'] = persons
            context['grades'] = grades
            return context
        return context


class PersonDisplayView(generic.DetailView):
    """
    Class to get a specific Person object based on the username.

    **DetailView:**
        Inherits Django's DetailView displaying a single Person Object
    :return: Person object

    """
    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"

    def get_context_data(self, **kwargs):
        """
        Function that adds a form to the context without overriding it.

        :param kwargs: keyword-arguments
        :return: The updated context
        """
        context = super(PersonDisplayView, self).get_context_data(**kwargs)
        context['form'] = ChangePassword()
        return context


class PersonDetailView(SchoolCheck, View):
    """
    View that handles PersonDisplayView (HTTP GET) and the ChangePasswordView (HTTP POST), this view is not displayed

    **SchoolCheck:**
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
    form_class = ChangePassword
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

    **RoleCheck:**
        Permission check, only allows teachers, administrators and school administrators.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated
    """

    login_url = reverse_lazy('login')
    role = 1
    template_name = 'administration/person_form.html'
    form_class = PersonForm
    success_url = reverse_lazy('administration:personList')

    def get_initial(self):
        """
        Function that checks for preset Person values and sets them to the fields

        :return: List the preset values
        """

        if self.kwargs.get('grade_pk'):
            self.success_url = reverse_lazy('administration:gradeDetail',
                                            kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                    'grade_pk': self.kwargs.get('grade_pk')})
            return {'role': self.role, 'grades': self.kwargs.get('grade_pk')}

    def form_valid(self, form):
        """
        Function that overrides form_valid and saves a new person object to the database.

        :param form: References to the model form.
        :return: calls super
        """

        person = form.save(commit=False)
        if self.request.user.role == 3:
            if person.role > 3 or person.role < 1:
                return super(PersonCreateView, self).form_invalid(form)
        username = Person.createusername(person)
        person.username = username
        person.set_password('ntnu123')
        person.save()
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

    **SchoolCheck:**
        Permission check.
    **UpdateView:**
        Inherits Django's Update that displays a form for updating a specific object and
        saving the form when validated.
    """

    template_name = 'administration/person_form.html'
    login_url = reverse_lazy('login')
    form_class = PersonForm
    model = Person
    slug_field = "username"

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
        else:
            context['schools'] = School.objects.all()
            context['gradesInfo'] = Grade.objects.all()
        if self.kwargs.get('grade_pk'):
            context['fromGrade'] = Grade.objects.get(id=self.kwargs.get('grade_pk'))
        return context


class PersonDeleteView(SchoolAdministratorCheck, generic.DeleteView):
    slug_field = 'username'
    model = Person
    success_url = reverse_lazy('administration:personList')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SchoolListView(SchoolAdministratorCheck, generic.ListView):
    """
    Class to list out all School objects

    **SchoolAdministratorCheck:**
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

    **SchoolCheck:**
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

    **AdministratorCheck:**
        inherited permission check
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
        username = person.createusername()
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
        context['administratorForm'] = SchoolAdministrator()
        return context


class SchoolUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update information about a school object based on the school_id.

    **SchoolCheck:**
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
        context['administratorForm'] = SchoolAdministrator()
        return context


class GradeDisplay(generic.DetailView, views.AjaxResponseMixin):
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
        Function that adds a person object and a FileUpload form to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(GradeDisplay, self).get_context_data(**kwargs)
        context['persons'] = Person.objects.filter(grades__id=self.kwargs['grade_pk'])
        context['schools'] = School.objects.all()
        context['grades'] = Grade.objects.all().exclude(id=self.kwargs['grade_pk'])
        context['existingStudents'] = Person.objects.filter(role=1, is_active=1).exclude(
            grades__id=self.kwargs['grade_pk'])
        context['existingTeachers'] = Person.objects.filter(role=2, is_active=1).exclude(
            grades__id=self.kwargs['grade_pk'])
        context['form'] = FileUpload()
        return context


class FileUploadView(generic.FormView):
    """
    Class that handles uploading excel files and creating Person objects from them
    """

    template_name = 'administration/grade_detail.html'
    form_class = FileUpload
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
                username = Person.createusername(person)
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
        return reverse('administration:gradeDetail', kwargs={'school_pk': self.kwargs.get('school_pk'),
                                                             'grade_pk': self.kwargs.get('grade_pk')})


class GradeDetailView(SchoolCheck, View):
    """
    View that handles GradeDisplay and the FileUploadView, this view is not displayed

    **SchoolCheck:**
        Permission check
    """

    def get(self, request, *args, **kwargs):
        """
        Redirects to the GradeDisplay

        :param request: request that was sent to GradeDetailView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the GradeDisplay with the same parameters that this method got
        """
        view = GradeDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Redirects to the FileUploadView

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

    **ScoolCheck:**
        inherited permission check
    **CreateView: Inherits generic.CreateView that displays a form for creating a object and
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

        return super(GradeCreateView, self).form_valid(form)


class GradeUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update a Grade object

    :param SchoolCheck: inherited permission check
    :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'is_active']
    pk_url_kwarg = 'grade_pk'

    def get_success_url(self):
        return reverse_lazy('administration:schoolDetail', kwargs={'school_pk': self.kwargs.get('school_pk')})


class GradeListView(RoleCheck, generic.ListView):
    """
    Class that displays a list of grade objects
    """
    login_url = reverse_lazy('login')
    template_name = 'administration/gradeList.html'

    def get_queryset(self):
        return Grade.objects.filter(person__username=self.request.user.username)


class GroupListView(AdministratorCheck, generic.ListView):
    template_name = 'administration/group_list.html'
    model = Gruppe


class GroupDetailView(AdministratorCheck, generic.DetailView):
    template_name = 'administration/group_detail.html'
    model = Gruppe
    pk_url_kwarg = 'group_pk'


class GroupCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    model = Gruppe
    fields = ['group_name', 'persons', 'is_active', 'visible']
    template_name = 'administration/group_form.html'
    success_url = reverse_lazy('administration:groupList')

    def get_ajax(self, request, *args, **kwargs):
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
        context = super(GroupCreateView, self).get_context_data(**kwargs)
        context['schools'] = School.objects.all()
        context['grades'] = Grade.objects.all()
        context['students'] = Person.objects.filter(role=1)
        return context

    def form_valid(self, form):
        gruppe = form.save(commit=False)
        gruppe.creator_id = self.request.user.id
        return super(GroupCreateView, self).form_valid(form)


class GroupUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update a Group object

    :param SchoolCheck: inherited permission check
    :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    model = Gruppe
    template_name = 'administration/group_form.html'
    fields = ['group_name', 'is_active', 'persons', 'visible']
    pk_url_kwarg = 'group_pk'

    def get_success_url(self):
        return reverse_lazy('administration:groupDetail', kwargs={'group_pk': self.kwargs.get('group_pk')})

    def get_context_data(self, **kwargs):
        context = super(GroupUpdateView, self).get_context_data(**kwargs)
        context['schools'] = School.objects.all()
        context['grades'] = Grade.objects.all()
        context['students'] = Person.objects.filter(role=1)
        return context
