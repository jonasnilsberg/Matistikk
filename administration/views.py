from django.views import generic
from braces import views
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Person, School, Grade
from django.contrib import messages
from django.views import View
from .forms import PersonForm, FileUpload, ChangePassword, SchoolForm, SchoolAdministrator
from django.shortcuts import render, render_to_response
import datetime
from django.utils.safestring import mark_safe
import re

# Create your views here.
from django.http import JsonResponse


class AdministratorCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has administrator privileges.
    """
    def test_func(self, user):
        if self.request.user.role == 4:
            return True
        return False


class RoleCheck(views.UserPassesTestMixin):

    def test_func(self, user):
        role = [2, 3, 4]
        if self.request.user.role in role:
            return True


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
                print(grades_teacher)
                print(grades)
                for grade_teacher in grades_teacher:
                    for grade in grades:
                        if grade_teacher == grade:
                            return True
            elif self.kwargs.get('slug'):
                grades = self.request.user.grades.all()
                print(grades)
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
        if self.request.user.role == 3 or self.request.user.role == 4:
            return True
        return False


class MyPageDetailView(views.UserPassesTestMixin, generic.FormView):
    """
    View that shows a user information about itself and allows them to change their password.
    :param views.UserPassesTestMixin: permission check, is overridden by the test_func function
    """
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
        """
        Checks if the form that has been posted is valid
        :param form: django form
        :return: calls MypageDetailView with form_valid and the form
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
        Function that adds a person object to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(MyPageDetailView, self).get_context_data(**kwargs)
        context['person'] = Person.objects.get(username=self.kwargs.get('slug'))
        return context


class PersonListView(RoleCheck, generic.ListView):
    """
    Class that lists all the users in the system, can only be accessed by administrators.

    :param SchoolAdministratorCheck: permission check, only allows administrators and school administrators
    :param generic.ListView: Inherits generic.ListView that makes a page representing a list of objects.
    :return: List of person objects
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/person_list.html'
    model = Person

    def get_context_data(self, **kwargs):
        """
        Function that adds a person object to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(PersonListView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            persons = Person.objects.filter(grades__school_id__in=schools).distinct()
            context['object_list'] = persons
            return context
        if self.request.user.role == 2:
            grades = self.request.user.grades.all()
            print(grades)
            persons = Person.objects.filter(grades__in=grades).distinct()
            context['object_list'] = persons
            return context
        return context


class PersonDisplayView(generic.DetailView):
    """
    Class to get a specific Person based on the username

    :param generic.DetailView: inherits from djangos DetailView displaying a single Person Object
    :return: Person object

    """

    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"

    def get_context_data(self, **kwargs):
        """
        Function that adds a form to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(PersonDisplayView, self).get_context_data(**kwargs)
        context['form'] = ChangePassword()
        return context


class PersonDetailView(SchoolCheck, View):
    """
    View that handles PersonDisplayView and the ChangePasswordView, this view is not displayed
    :param SchoolCheck:  Permission check
    """

    def get(self, request, *args, **kwargs):
        """
        Redirects to the PersonDisplayView
        :param request: request that was sent to PersonDetaiLView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the PersonDisplayView with the same parameters that this method got
        """
        view = PersonDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        redirects to ChangePasswordView
        :param request: request that was sent to PersonDetaiLView
        :param args:  Arguments that were sent with the request
        :param kwargs: keyword-arguments
        :return: returns the ChangePasswordView with the same parameters that this method got
        """
        view = ChangePasswordView.as_view()
        return view(request, *args, **kwargs)


class ChangePasswordView(generic.FormView):
    """
    View that handles changing password for a different user than the one that is logged in.
    """
    template_name = 'administration/person_detail.html'
    form_class = ChangePassword
    model = Person
    slug_field = 'username'

    def get_success_url(self):
        return reverse('administration:personDetail', kwargs={'slug': self.kwargs.get('slug')})

    def form_valid(self, form):
        """
        Function that checks if the submitted text is correct, and if correct sets this at the new password of the user.
        If the passwords don't match it returns a errormessage.
        :param form: References to the model form.
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
            messages.error(self.request,'Feltene var ikke like. Passordet ble ikke oppdatert')
        return super(ChangePasswordView, self).form_valid(form)


class PersonCreateView(RoleCheck, generic.CreateView):
    """
    Creates a Person object

    :param SchoolCheck: Inherited permission check
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
        username = Person.createusername(person)

        person.username = username
        person.set_password('ntnu123')
        person.save()
        return super(PersonCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Function that adds data to the context without overriding it, adds different data depending on users role
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(PersonCreateView, self).get_context_data(**kwargs)
        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            print(schools)
            print(Grade.objects.filter(school_id__in=schools))
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


class PersonUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class that updates a Person object

    :param SchoolCheck: inherited permission check
    :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
        saving the form when validated.
    """

    template_name = 'administration/person_form.html'
    login_url = reverse_lazy('login')
    form_class = PersonForm
    model = Person
    slug_field = "username"

    def get_context_data(self, **kwargs):
        """
        Function that adds data to the context without overriding it, adds different data depending on users role
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


class SchoolListView(SchoolAdministratorCheck, generic.ListView):
    """
    Class to list out all School objects

    :param SchoolAdministratorCheck: Inherited permission check
    :param generic.ListView: Inherits generic.ListView that represents a page containing a list of objects
    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """
        Function that adds a school object to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        if self.request.user.role == 3:
            context = super(SchoolListView, self).get_context_data(**kwargs)
            context['object_list'] = School.objects.filter(school_administrator=self.request.user.id)
            return context
        return super(SchoolListView, self).get_context_data(**kwargs)


class SchoolDetailView(SchoolCheck, generic.DetailView):
    """
    class that displays information about a specific school

    :param SchoolCheck: Inherited permission check
    """
    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_detail.html'
    pk_url_kwarg = 'school_pk'

    def get_context_data(self, **kwargs):
        """
        Function that adds a grade object to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(SchoolDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.filter(school_id=self.kwargs['school_pk'])
        return context


class SchoolCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    """
    Class to create a School object

    :param AdministratorCheck: inherited permission check
    :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
        saving the form when validated
    """

    login_url = reverse_lazy('login')
    template_name = 'administration/school_form.html'
    form_class = SchoolForm
    success_url = reverse_lazy('administration:schoolList')

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax post and finds the searched for Persons.
            :param self:
                References to the class itself and all it's variables
            :param request:
                The request
            :return: List of person objects
        """
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        date_of_birth = request.POST['date_of_birth']
        sex = request.POST['sex']
        person = Person(first_name=first_name, last_name=last_name, email=email, sex=sex)
        person.date_of_birth = datetime.datetime.strptime(date_of_birth, "%d.%m.%Y").strftime("%Y-%m-%d")
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
        context = super(SchoolCreateView, self).get_context_data(**kwargs)
        context['administratorForm'] = SchoolAdministrator()
        return context


class SchoolUpdateView(SchoolCheck, generic.UpdateView):
    """
    Class to update information about a school object

    :param SchoolCheck: inherited permission check
    :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a object and
        saving the form when validated.
    """

    login_url = reverse_lazy('login')
    model = School
    template_name = 'administration/school_form.html'
    form_class = SchoolForm
    pk_url_kwarg = 'school_pk'

    def get_context_data(self, **kwargs):
        context = super(SchoolUpdateView, self).get_context_data(**kwargs)
        context['administratorForm'] = SchoolAdministrator()
        return context


class GradeDisplay(generic.DetailView):
    """
    Class that displays information about a single grade object

    :param SchoolCheck: inherited permission check
    :param generic.DetailView: Inherits generic.DetailView that makes a page representing a specific object.
    """
    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_detail.html'
    success_url = '/'
    pk_url_kwarg = 'grade_pk'

    def get_context_data(self, **kwargs):
        """
        Function that adds a person object and a FileUpload form to the context without overriding it
        :param kwargs: keyword-arguments
        :return: returns the updated context
        """
        context = super(GradeDisplay, self).get_context_data(**kwargs)
        context['persons'] = Person.objects.filter(grades__id=self.kwargs['grade_pk'])
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
    :param SchoolCheck:  Permission check
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

    :param ScoolCheck: inherited permission check
    :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
        saving the form when validated
    """

    login_url = reverse_lazy('login')
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'tests']

    def form_valid(self, form):
        """
        Overrides generic.CreateViews form_valid and saves a grade to a specific school
        :param form: represents the form object
        :return: calls super
        """
        self.success_url = reverse_lazy('administration:schoolDetail', kwargs={'school_pk': self.kwargs.get('school_pk')})
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
    fields = ['grade_name', 'tests', 'is_active']
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
