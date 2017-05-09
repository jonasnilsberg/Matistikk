from django.views import generic
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from .forms import CreateTaskForm, CreateCategoryForm, CreateTestForm, CreateAnswerForm
from .models import Task, MultipleChoiceTask, Category, GeogebraTask, Test, TaskOrder, TaskCollection, Answer, \
    GeogebraAnswer
from braces import views
from django.http import JsonResponse, HttpResponseBadRequest
from administration.models import Grade, Person, Gruppe, School
import json
from django.db.models import Q
import django_excel as excel
from administration.views import AdministratorCheck, RoleCheck
import datetime

import random
from django.http import HttpResponseRedirect


class AnswerCheck(views.UserPassesTestMixin):
    """
    Checks if the logged in user has privileges to see the answer.

     **UserPassesTestMixin:**
        Mixin from :ref:`Django braces` that check is the logged in user passes the test given in :func:`test_func`.
    """

    def test_func(self, user):
        """
            :param user: Person that has to pass the test.
            :return: True if the user logged in as an administrator.
        """
        if user.is_authenticated():
            role = [2, 3, 4]
            if user.role in role:
                return True
            elif user.role == 1:
                if self.kwargs.get('slug'):
                    answer_user = self.kwargs.get('slug')
                    if answer_user == user.username:
                        return True
                else:
                    test_id = self.kwargs.get('test_pk')
                    if Person.objects.filter(id=user.id, tests__id=test_id).exists():
                        return True
                    elif Grade.objects.filter(person=user, tests__id=test_id).exists():
                        return True
                    elif Gruppe.objects.filter(persons=user, tests__id=test_id).exists():
                        return True
        return False


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """
    Class that displays the home page if logged in.

    **LoginRequiredMixin**
        Mixin from :ref:`Django braces` that check if the user is logged in.
    **TemplateView:**
        Inherits generic.Template that makes a page representing a specific template.
    """
    login_url = '/login/'
    template_name = 'maths/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.count()
        context['users'] = Person.objects.count()
        context['tests'] = TaskCollection.objects.count()
        context['schools'] = School.objects.count()
        context['grades'] = Grade.objects.count()
        context['groups'] = Gruppe.objects.count()

        if self.request.user.role == 1:
            answers = Answer.objects.filter(user=self.request.user)
            tests = Test.objects.filter(
                Q(person=self.request.user) | Q(grade__in=self.request.user.grades.all()) | Q(
                    gruppe__in=self.request.user.gruppe_set.all())).distinct()
            answered = tests.filter(answer__in=answers).distinct().order_by('-answer__date_answered')
            context['answered'] = answered
            notanswered = []
            for test in tests:
                if test not in answered:
                    notanswered.append(test)
            context['notanswered'] = notanswered
        return context


class EquationEditorView(LoginRequiredMixin, generic.TemplateView):
    """
    Allows users to input math into the editor.

    **LoginRequiredMixin**
        Mixin from :ref:`Django braces` that check if the user is logged in.
    **TemplateView:**
        Inherits generic.Template that makes a page representing a specific template.
    """
    login_url = '/login/'
    template_name = 'maths/equation_editor.html'


class TaskCreateView(AdministratorCheck, generic.CreateView):
    """
    Class that creates a task.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_form.html'
    form_class = CreateTaskForm
    success_url = reverse_lazy('maths:taskList')

    def get_context_data(self, **kwargs):
        """
            Function that adds all category objects and a form to create a new category to the context without
            overriding it.

            :param kwargs: Keyword arguments.
            :return: Returns the updated context.
        """
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['categoryForm'] = CreateCategoryForm()
        return context

    def form_valid(self, form):
        """
        Function that checks if the submitted :ref:`CreateTaskForm` is correct. If correct adds the logged in user as
        the author and creates the task with its extra information.

        :param form: References to the filled out model form.
        :return: calls super with the new form.
        """
        task = form.save(commit=False)
        task.author = self.request.user
        task.save()

        if task.answertype == 2:
            options = self.request.POST['options']
            optiontable = options.split('|||||')
            correct = optiontable[0]
            x = 1
            for option in optiontable[1:]:
                if int(correct) == x:
                    multiplechoice = MultipleChoiceTask(option=option, task=task, correct=True)
                else:
                    multiplechoice = MultipleChoiceTask(option=option, task=task, correct=False)
                multiplechoice.save()
                x += 1

        if task.extra:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            geogebratask = GeogebraTask(base64=base64, preview=preview, task=task)
            geogebratask.save()
        return super(TaskCreateView, self).form_valid(form)


class CategoryListView(AdministratorCheck, generic.ListView):
    """
    Class that displays a template containing all category objects.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    model = Category
    template_name = 'maths/category_list.html'


class CategoryCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    """
    Class that creates a category.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    model = Category
    fields = ['category_title']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax request, creates a new category and returns the
            category_id.

            :param request: Request that was sent to CategoryCreateView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the category id.
        """
        category_title = request.POST['category']
        category = Category(category_title=category_title)
        category.save()
        data = {
            'category_id': category.id
        }
        return JsonResponse(data)


class CategoryUpdateView(AdministratorCheck, generic.UpdateView):
    """
    Class that updates a category.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    model = Category
    fields = ['category_title']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')
    pk_url_kwarg = 'category_pk'


class TaskListView(RoleCheck, views.AjaxResponseMixin, generic.ListView):
    """
    Class that displays a template containing all task objects.

     :func:`RoleCheck`:
        Permission check, only allows teachers, administrators and school administrators.
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_list.html'
    model = Task

    def get_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the get request is an ajax request and returns the all the necessary information
            around a specific task.

            :param request: Request that was sent to TaskListView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the necessary Task information.
        """
        multiplechoice = []
        task_id = request.GET['task_id']
        task = Task.objects.get(id=task_id)
        data = {
            'task_title': task.title,
            'task_text': task.text,
            'task_reasoning': task.reasoning,
            'task_extra': task.extra,
            'task_answertype': task.answertype,
            'options': multiplechoice
        }
        if task.extra:
            geogebra = GeogebraTask.objects.get(task_id=task_id)
            data['geogebra_preview'] = geogebra.preview
        if task.answertype == 2:
            multiplechoice_list = MultipleChoiceTask.objects.filter(task_id=task_id)
            for option in multiplechoice_list:
                multiplechoice.append({
                    "option": option.option,
                    "correct": option.correct,
                })
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all category and geogebratask objects to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['geogebratask'] = GeogebraTask.objects.all()
        return context


class TaskUpdateView(AdministratorCheck, generic.UpdateView):
    """
    Class that updates a task.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_update.html'
    model = Task
    form_class = CreateTaskForm
    pk_url_kwarg = 'task_pk'
    success_url = reverse_lazy('maths:taskList')

    def get_context_data(self, **kwargs):
        """
            Function that adds the multiple choice options and geogebra to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        if GeogebraTask.objects.filter(task=self.kwargs.get("task_pk")):
            context['geogebra'] = GeogebraTask.objects.filter(task=self.kwargs.get("task_pk"))
        if MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk")):
            context['options'] = MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk"))

        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """
            Function that checks if the submitted :ref:`CreateTaskForm` is correct. If correct it updates the task with
            the new values and creates new multiple choice options or geogebra if it's added.

            :param form: References to the filled out model form.
            :return: calls super with the new form.
        """
        task = form.save(commit=False)
        task.save()

        if task.extra:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            geotask = GeogebraTask.objects.filter(task=task)
            if geotask.count() > 0:
                geogebratask = GeogebraTask.objects.get(task=task)
                geogebratask.base64 = base64
                geogebratask.preview = preview
                geogebratask.save()
            else:
                geogebratask = GeogebraTask(task=task, base64=base64, preview=preview)
                geogebratask.save()

        if task.answertype == 2:
            options = self.request.POST['options']
            optiontable = options.split('|||||')
            correct = optiontable[0]
            taskoptions = MultipleChoiceTask.objects.filter(task=task)
            newoptions = (len(optiontable) - 1) - len(taskoptions)

            x = 1
            for taskoption in taskoptions:
                if int(correct) == x:
                    taskoption.correct = True
                    taskoption.option = optiontable[x]
                else:
                    taskoption.correct = False
                    taskoption.option = optiontable[x]
                taskoption.save()
                x += 1

            if newoptions > 0:
                for option in optiontable[len(optiontable) - newoptions:]:
                    if int(correct) == x:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=True)
                    else:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=False)
                    multiplechoice.save()
                    x += 1
        return super(TaskUpdateView, self).form_valid(form)


class TaskCollectionCreateView(AdministratorCheck, generic.CreateView):
    """
    Class that creates a taskCollection.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    template_name = 'maths/taskCollection_form.html'
    model = TaskCollection
    fields = ['test_name', 'tasks']

    def get_context_data(self, **kwargs):
        """
            Function that adds all the task and category objects to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionCreateView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """
            Function that checks if the submitted modelform is correct. If correct it adds the logged in user as author
            of the test and saves it.

            :param form: References to the filled out model form.
            :return: calls super with the new form.
        """
        task_collection = form.save(commit=False)
        task_collection.author = self.request.user
        task_collection.save()
        return super(TaskCollectionCreateView, self).form_valid(form)


class TaskCollectionListView(AdministratorCheck, generic.ListView):
    """
       Class that displays a template containing all taskCollection objects.

        :func:`AdministratorCheck`:
            inherited permission check, checks if the logged in user is an administrator.
       **ListView:**
           Inherits Django's ListView that makes a page representing a list of objects.
    """
    template_name = 'maths/taskCollection_list.html'
    model = TaskCollection


class TaskCollectionDetailView(AdministratorCheck, views.AjaxResponseMixin, generic.DetailView):
    """
    Class that displays information about a single taskCollection object based on the taskCollection_id.
    
    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **DetailView:**
        Inherits generic.DetailView that makes a page representing a specific object.
    """
    template_name = 'maths/taskCollection_detail.html'
    model = TaskCollection
    pk_url_kwarg = 'taskCollection_pk'

    def get_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the get request is an ajax request and returns the all the students, teachers, 
            grades and groups associated with a test.

            :param request: Request that was sent to TaskCollectionDetailView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the students, teachers, grades and groups. 
        """
        students = []
        teachers = []
        grades = []
        groups = []
        test = Test.objects.get(id=request.GET['published_id'])
        student_list = Person.objects.filter(tests__exact=test, role=1)
        teacher_list = Person.objects.filter(tests__exact=test, role=2)
        grade_list = Grade.objects.filter(tests__exact=test)
        group_list = Gruppe.objects.filter(tests__exact=test)
        for student in student_list:
            students.append({
                'username': student.username,
                'first_name': student.first_name,
                'last_name': student.last_name
            })
        for teacher in teacher_list:
            teachers.append({
                'username': teacher.username,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name
            })
        for grade in grade_list:
            grades.append({
                'grade_name': grade.grade_name,
                'school': grade.school.school_name,
                'id': grade.id,
                'school_id': grade.school.id
            })
        for group in group_list:
            groups.append({
                'group_name': group.group_name,
                'grade': group.grade.school.school_name + " - " + group.grade.grade_name,
                'creator': group.creator.get_full_name(),
                'id': group.id

            })
        data = {
            'students': students,
            'teachers': teachers,
            'grades': grades,
            'groups': groups
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all the categories and published test from the specified taskCollection to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionDetailView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['publishedTests'] = Test.objects.filter(task_collection_id=self.kwargs.get('taskCollection_pk'))
        return context


class TestCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
    """
    Class that creates a test.

    :func:`AdministratorCheck`:
        inherited permission check, checks if the logged in user is an administrator.
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    form_class = CreateTestForm
    template_name = 'maths/test_form.html'

    def get_success_url(self):
        """
        Function that sets the success url.
        :return: Success url
        """
        success = reverse_lazy('maths:taskCollectionDetail',
                               kwargs={'taskCollection_pk': self.kwargs.get('taskCollection_pk')})
        return success

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax request, and updates the dueDate for the specified test.

            :param request: Request that was sent to TestCreateView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the new dueDate.
        """
        test_id = request.POST['id']
        test = Test.objects.get(id=test_id)
        new_due = request.POST['dueDate']
        test.dueDate = new_due
        test.save()
        data = {
            'dueDate': new_due
        }
        return JsonResponse(data)

    def get_initial(self):
        """
        Function that checks for preset values and sets them to the fields.

        :return: List of the preset values.
        """
        return {'task_collection': self.kwargs.get('taskCollection_pk')}

    def get_context_data(self, **kwargs):
        """
            Function that adds all the students, teachers, grades, groups and schools to the context without 
            overriding it.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TestCreateView, self).get_context_data(**kwargs)
        context['taskcollection'] = TaskCollection.objects.get(id=self.kwargs.get('taskCollection_pk'))
        context['grades'] = Grade.objects.all()
        context['teachers'] = Person.objects.filter(role=2)
        context['students'] = Person.objects.filter(role=1)
        context['schools'] = School.objects.all()
        context['groups'] = Gruppe.objects.all()
        return context

    def form_valid(self, form):
        """
            Function that checks if the submitted :ref:`CreateTestForm` is correct. If correct it adds the test to the 
            to the selected students, teachers, grades, groups and schools. Checks if randomOrder was selected and 
            and creates the TaskOrder if that's the case. 
            
            :param form: References to the filled out form.
            :return: calls super with the new form.
        """
        test = form.save(commit=False)
        test.save()
        data = form.cleaned_data
        for person in data['persons']:
            person.tests.add(test)
        for grade in data['grades']:
            grade.tests.add(test)
        for group in data['groups']:
            group.tests.add(test)
        if not data['randomOrder']:
            order_list = data['order']
            order_table = order_list.split('|||||')
            x = 1
            for order in order_table:
                print(order)
                taskorder = TaskOrder(test=test, task_id=order, order=x)
                taskorder.save()
                x += 1
        return super(TestCreateView, self).form_valid(form)


class TestDetailView(RoleCheck, views.AjaxResponseMixin, generic.DetailView):
    """
    Class that displays information about a single test object based on the test_id.

     :func:`RoleCheck`:
        Permission check, only allows teachers, administrators and school administrators.
    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **DetailView:**
        Inherits generic.DetailView that makes a page representing a specific object.
    """
    model = Test
    template_name = 'maths/test_detail.html'
    pk_url_kwarg = 'test_pk'

    def get_context_data(self, **kwargs):
        """
            Function that adds more to the context depending on the logged in user or the previous destination without 
            overriding it. 

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TestDetailView, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        if self.kwargs.get('grade_pk'):
            grade = Grade.objects.get(id=self.kwargs.get('grade_pk'))
            context['students'] = Person.objects.filter(grades=grade)
            context['fromGrade'] = grade
        elif self.kwargs.get('group_pk'):
            group = Gruppe.objects.get(id=self.kwargs.get('group_pk'))
            context['students'] = Person.objects.filter(gruppe=group)
            context['fromGroup'] = group
        elif self.request.user.role == 2:
            grades = Grade.objects.filter(person=self.request.user)
            context['students'] = Person.objects.filter(tests__exact=test, role=1, grades__in=grades).distinct()
            print(context['students'])
            context['grades'] = grades.filter(tests__exact=test)
            context['groups'] = Gruppe.objects.filter(tests__exact=test, grade__in=grades)
        else:
            context['students'] = Person.objects.filter(tests__exact=test, role=1)
            context['teachers'] = Person.objects.filter(tests__exact=test, role=2)
            context['grades'] = Grade.objects.filter(tests__exact=test)
            context['groups'] = Gruppe.objects.filter(tests__exact=test)
            context['allstudents'] = Person.objects.filter(role=1).exclude(tests__exact=test)
            context['allteachers'] = Person.objects.filter(role=2).exclude(tests__exact=test)
            context['allgrades'] = Grade.objects.all().exclude(tests__exact=test)
            context['allgroups'] = Gruppe.objects.all().exclude(tests__exact=test)
            context['allschools'] = School.objects.all()
        return context


class AnswerCreateView(AnswerCheck, generic.FormView):
    """
   Class for creating answers for all the tasks in a test.

    :func:`AnswerCheck`:
        inherited permission check, checks if the logged in user can answer the test.
    **FormView**
       A view that displays a form.
    """
    form_class = CreateAnswerForm
    template_name = 'maths/answer_form.html'

    def get_success_url(self):
        """
            Function that returns the success url.
            :return: success url.
        """
        return reverse_lazy('maths:index')

    def get_context_data(self, **kwargs):
        """
            Function that adds all information needed about a specific test and adds a form for each task in the test
            without overriding it. 

            :param kwargs: Keyword arguments
            :return: Updated context
        """
        context = super(AnswerCreateView, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        geogebratasks = GeogebraTask.objects.filter(task__in=test.task_collection.tasks.all())
        options = MultipleChoiceTask.objects.filter(task__in=test.task_collection.tasks.all())
        randomtest = sorted(test.task_collection.tasks.all(), key=lambda x: random.random())
        context['test'] = test
        context['randomtest'] = randomtest
        context['geogebratask'] = geogebratasks
        context['options'] = options
        z = 0
        forms = []
        for task in test.task_collection.tasks.all():
            forms.append(CreateAnswerForm(prefix="task" + str(z)))
            z += 1
        context['formlist'] = forms
        return context

    def post(self, request, *args, **kwargs):
        """
            Handles the HTTP POST methods and creates an answer for each task in the test.
    
            :param request: Request that was sent to AnswerCreateView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: HttpResponseRedirect to the index page.
        """
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        y = 0
        for task in test.task_collection.tasks.all():
            text = request.POST["task" + str(y) + "-text"]
            reasoning = request.POST["task" + str(y) + "-reasoning"]
            taskid = request.POST["task" + str(y) + "-task"]
            timespent = request.POST["task" + str(y) + "-timespent"]
            task = Task.objects.get(id=taskid)
            answer = Answer(text=text, reasoning=reasoning, user=self.request.user, test=test, task=task,
                            timespent=timespent)
            answer.date_answered = datetime.datetime.now()
            answer.save()
            base64 = request.POST["task" + str(y) + "-base64answer"]
            geogebradata = request.POST["task" + str(y) + "-geogebradata"]
            if task.extra:
                geogebraanswer = GeogebraAnswer(answer=answer, base64=base64, data=geogebradata)
                geogebraanswer.save()
            y += 1
        url = reverse('maths:index')
        return HttpResponseRedirect(url)


class TestListView(RoleCheck, views.AjaxResponseMixin, generic.ListView):
    """
       Class that displays a template a list of test objects.
       
        :func:`RoleCheck`:
            Permission check, only allows teachers, administrators and school administrators.
       **AjaxResponseMixin:**
            This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
       **ListView:**
            Inherits Django's ListView that makes a page representing a list of objects.
    """
    model = Test
    template_name = 'maths/test_list.html'

    def get_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the get request is an ajax request and checks if the students, groups and / or grades
            are associated with the test.

            :param request: Request that was sent to TestListView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the a boolean table for students, teachers, grades and / or groups . 
        """
        test = Test.objects.get(id=request.GET['test'])
        grade_table = []
        group_table = []
        student_table = []
        grades = request.GET['grades']
        groups = request.GET['groups']
        students = request.GET['students']
        grade_list = json.loads(grades)
        group_list = json.loads(groups)
        student_list = json.loads(students)
        for grade_id in grade_list:
            if test.grade_set.filter(id=grade_id).exists():
                grade_table.append(True)
            else:
                grade_table.append(False)
        for group_id in group_list:
            if test.gruppe_set.filter(id=group_id).exists():
                group_table.append(True)
            else:
                group_table.append(False)
        for student_id in student_list:
            if test.person_set.filter(id=student_id).exists() or test.grade_set.filter(
                    person__id=student_id).exists() or test.gruppe_set.filter(persons__id=student_id).exists():
                student_table.append(True)
            else:
                student_table.append(False)
        data = {
            "grades": grade_table,
            'groups': group_table,
            'students': student_table
        }
        return JsonResponse(data)

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax request, adds the test to the selected students, grades
            and / or groups.

            :param request: Request that was sent to TestListView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing a boolean that says true.
        """
        test = Test.objects.get(id=request.POST['test'])
        grades = request.POST['grades']
        groups = request.POST['groups']
        students = request.POST['students']
        grade_list = json.loads(grades)
        group_list = json.loads(groups)
        student_list = json.loads(students)
        for grade_id in grade_list:
            grade = Grade.objects.get(id=grade_id)
            grade.tests.add(test)
        for group_id in group_list:
            group = Gruppe.objects.get(id=group_id)
            group.tests.add(test)
        for student_id in student_list:
            student = Person.objects.get(id=student_id)
            student.tests.add(test)
        data = {'success': True}
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that overrides the created object_list to only containing the users tests and adds all the 
            users grades to the context. 

            :param kwargs: Keyword arguments
            :return: Updated context
        """
        context = super(TestListView, self).get_context_data(**kwargs)
        user = Person.objects.get(username=self.kwargs.get('slug'))
        context['object_list'] = Test.objects.filter(person=user)
        context['grades'] = Grade.objects.filter(person=user)
        return context


class AnswerListView(AnswerCheck, generic.ListView):
    """
    Class that displays a list of answers for all the tasks in a specific test for a specific user.

    :func:`AnswerCheck`:
        inherited permission check, checks if the logged in user can answer the test.
    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    template_name = 'maths/answer_detail.html'

    def get_queryset(self):
        """
            Function that sets the query for getting the object_list. 
            
            :return: List of answer objects.
        """
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        person = Person.objects.get(username=self.kwargs.get('slug'))
        return Answer.objects.filter(test=test, user=person)

    def get_context_data(self, **kwargs):
        context = super(AnswerListView, self).get_context_data(**kwargs)
        if self.kwargs.get('grade_pk'):
            context['fromGrade'] = self.kwargs.get('grade_pk')
        return context


def export_data(request, test_pk):
    """
        Function that exports all answers for all tasks and users in a specific test.
        
        :param request: Request that was sent to export_data 
        :param test_pk: The id for the specific test.
        :return: Excel-file
    """
    if request.user.role is not 1:
        test = Test.objects.get(id=test_pk)
        answers = Answer.objects.filter(test=test)
        column_names = ['task_id', 'user_id', 'text', 'reasoning', 'timespent', 'date_answered']
        return excel.make_response_from_query_sets(answers, column_names, 'xlsx',
                                                   file_name=test.task_collection.test_name)
    else:
        array = ['#hackerman']
        return excel.make_response_from_array(array, 'xlsx', file_name='fasit')
