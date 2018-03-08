from django.views import generic
from django.contrib import messages
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from .forms import CreateTaskForm, CreateCategoryForm, CreateTestForm, CreateAnswerForm, CreateTaskLog, \
    CreateTestAnswerForm
from .models import Task, MultipleChoiceTask, Category, GeogebraTask, Test, TaskOrder, TaskCollection, Answer, \
    GeogebraAnswer, Item, MultipleChoiceOption, InputFieldTask, InputField, Directory, TaskLog, ImageTask, TestAnswer
from braces import views
from django.http import JsonResponse
from administration.models import Grade, Person, Gruppe, School
import json
from django.db.models import Q
import django_excel as excel
from administration.views import AdministratorCheck, RoleCheck
import random
from django.http import HttpResponseRedirect
from django.conf import settings
import re
from django.utils import formats
from django.utils import timezone


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
        test_id = self.kwargs.get('test_pk')
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
                    if Person.objects.filter(id=user.id, tests__id=test_id).exists():
                        return True
                    elif Grade.objects.filter(person=user, tests__id=test_id).exists():
                        return True
                    elif Gruppe.objects.filter(persons=user, tests__id=test_id).exists():
                        return True
        else:
            test = Test.objects.get(id=test_id)
            if test.public:
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
    login_url = settings.LOGIN_URL
    template_name = 'maths/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        # Fjern dette etter oppdatering -----------------------------------------------------------------------------
        # all_answers = Answer.objects.all()
        # for answer in all_answers:
        #    print(Answer.objects.filter(user__isnull=True, anonymous_user__isnull=True))
        #    if not answer.testAnswer:
        #        if answer.anonymous_user is not None:
        #            print("if - " + str(answer.user))
        #            if TestAnswer.objects.filter(test=answer.test, anonymous_user=answer.anonymous_user).exists():
        #                test_answer = TestAnswer.objects.get(test=answer.test, anonymous_user=answer.anonymous_user)
        #                answer.testAnswer = test_answer
        #                answer.save()
        #            else:
        #                test_answer = TestAnswer(test=answer.test, anonymous_user=answer.anonymous_user, status=3)
        #                test_answer.save()
        #                answer.testAnswer = test_answer
        #                answer.save()
        #        else:
        #           if TestAnswer.objects.filter(test=answer.test, user=answer.user).exists():
        #            test_answer = TestAnswer.objects.get(test=answer.test, user=answer.user)
        #            answer.testAnswer = test_answer
        #            answer.save()
        #        else:
        #            test_answer = TestAnswer(test=answer.test, user=answer.user, status=3)
        #            test_answer.save()
        #            answer.testAnswer = test_answer
        #            answer.save()
        # -----------------------------------------------------------------------------------------------------------
        if self.request.user.role == 2:
            user = Person.objects.get(username=self.request.user.username)
            tests = Test.objects.filter(person=user)
            context['tests'] = tests
            context['lastanswers'] = TestAnswer.objects.filter(test__in=tests, user__isnull=False, status=3).order_by('-id')
        if self.request.user.role == 4:
            context['answers'] = TestAnswer.objects.filter(status=3).count()
            context['users'] = Person.objects.count()
            context['tests'] = TaskCollection.objects.count()
            context['schools'] = School.objects.count()
            context['grades'] = Grade.objects.count()
            context['groups'] = Gruppe.objects.count()
            context['lasttests'] = Test.objects.all().order_by('-id')[:15]
            context['lastanswers'] = TestAnswer.objects.filter(status=3).order_by('-id')[:15]

        if self.request.user.role == 3:
            schools = School.objects.filter(school_administrator=self.request.user.id)
            persons = Person.objects.filter(grades__school_id__in=schools).distinct()
            context['persons'] = persons
            context['schools'] = schools
            grades = Grade.objects.filter(school__in=schools)
            context['grades'] = grades

        if self.request.user.role == 1:
            answeredTests = []
            test_answers = TestAnswer.objects.filter(user=self.request.user, status=3)
            tests = Test.objects.filter(
                Q(person=self.request.user) | Q(grade__in=self.request.user.grades.all()) | Q(
                    gruppe__in=self.request.user.gruppe_set.all())).distinct()
            print(tests)
            answered = tests.filter(testanswer__in=test_answers).distinct().order_by('-answer__date_answered')
            for test in answered:
                if test not in answeredTests:
                    answeredTests.append(test)

            context['answered'] = answeredTests
            notanswered = []
            for test in tests:
                if test not in answeredTests:
                    notanswered.append(test)
            context['notanswered'] = notanswered
        return context


class EquationEditorView(generic.TemplateView):
    """
    Allows users to input math into the editor.

    **LoginRequiredMixin**
        Mixin from :ref:`Django braces` that check if the user is logged in.
    **TemplateView:**
        Inherits generic.Template that makes a page representing a specific template.
    """
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
    success_url = reverse_lazy('maths:directoryRoot')

    def get_initial(self):
        if self.kwargs.get('directory_pk'):
            data = {
                'directory': self.kwargs.get('directory_pk')
            }
            return data
        else:
            directory = Directory.objects.get(parent_directory=None)
            data = {
                'directory': directory.id
            }
            return data

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
        self.success_url = reverse_lazy('maths:directoryDetail', kwargs={
            'directory_pk': task.directory.id
        })
        task.author = self.request.user
        messages.success(self.request, 'Oppgave med navnet: ' + task.title + " ble opprettet.")
        variable_task = self.request.POST['variables']
        if variable_task:
            task.variableTask = True
        task.save()
        item = Item(task=task, variables=variable_task)
        item.save()
        if task.answertype == 2:
            options = self.request.POST['options']
            correct = self.request.POST['correct']
            questions = self.request.POST['questions']
            radio_or_check = self.request.POST['radioOrCheck']
            option_split = options.split('<--->')
            correct_split = correct.split('<--->')
            question_split = questions.split('|||||')
            radio_or_check_split = radio_or_check.split('|||||')
            x = 0
            for question in question_split:
                multiple_choice_task = MultipleChoiceTask(question=question, task=task)
                if radio_or_check_split[x] == 'true':
                    multiple_choice_task.checkbox = True
                else:
                    multiple_choice_task.checkbox = False
                multiple_choice_task.save()
                multiple_choice_options = option_split[0].split('|||||')
                multiple_choice_options_correct = correct_split[0].split('|||||')
                for i in range(0, len(multiple_choice_options)):
                    multiple_choice_option = MultipleChoiceOption(MutipleChoiceTask=multiple_choice_task,
                                                                  option=multiple_choice_options[i])
                    if multiple_choice_options_correct[i] == 'true':
                        multiple_choice_option.correct = True
                    else:
                        multiple_choice_option.correct = False
                    multiple_choice_option.save()
                option_split.pop(0)
                correct_split.pop(0)
                x += 1
        elif task.answertype == 4:
            input_questions = form.cleaned_data['inputQuestion']
            inputfield = form.cleaned_data['inputField']
            inputlength = form.cleaned_data['inputLength']
            inputcorrect = form.cleaned_data['inputCorrect']
            inputfraction = form.cleaned_data['inputFraction']
            inputfield_split = inputfield.split('<--->')
            inputlength_split = inputlength.split('<--->')
            inputcorrect_split = inputcorrect.split('<--->')
            inputfraction_split = inputfraction.split('<--->')
            input_questions_split = input_questions.split('|||||')
            x = 1
            for i in range(0, len(input_questions_split)):
                inputfieldtask = InputFieldTask(task=task, question=input_questions_split[i])
                inputfieldtask.save()
                inputfields = inputfield_split[i].split('|||||')
                input_length = inputlength_split[i].split('|||||')
                input_correct = inputcorrect_split[i].split('|||||')
                input_fraction = inputfraction_split[i].split('|||||')
                for y in range(0, len(inputfields)):
                    input = InputField(inputFieldTask=inputfieldtask, title=inputfields[y], inputnr=x,
                                       correct=input_correct[y], inputlength=input_length[y])
                    if input_fraction[y] == "1":
                        input.fraction = True
                    input.save()
                    x += 1
        if task.extra == 1:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            height = self.request.POST['height']
            width = self.request.POST['width']
            xmin = self.request.POST['xmin']
            xmax = self.request.POST['xmax']
            ymin = self.request.POST['ymin']
            ymax = self.request.POST['ymax']
            yratio = self.request.POST['yratio']
            xstep = self.request.POST['xstep']
            ystep = self.request.POST['ystep']
            show_menu_bar = form.cleaned_data['showMenuBar']
            enable_label_drags = form.cleaned_data['enableLabelDrags']
            enable_shift_drag_zoom = form.cleaned_data['enableShiftDragZoom']
            enable_right_click = form.cleaned_data['enableRightClick']
            algebra_input_field = form.cleaned_data['algebraInputField']
            geogebratask = GeogebraTask(base64=base64, preview=preview, task=task, height=height, width=width,
                                        showMenuBar=show_menu_bar, enableLabelDrags=enable_label_drags,
                                        enableShiftDragZoom=enable_shift_drag_zoom, enableRightClick=enable_right_click,
                                        xmax=xmax, xmin=xmin, ymax=ymax, ymin=ymin, yratio=yratio, xstep=xstep,
                                        ystep=ystep, algebraInputField=algebra_input_field)
            geogebratask.save()
        elif task.extra == 2:
            image = form.cleaned_data['imageFile']
            image_task = ImageTask(task=task, image=image, author=self.request.user)
            image_task.save()
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
        category, created = Category.objects.get_or_create(
            category_title=category_title
        )
        data = {
            'category_id': category.id,
            'created': created
        }
        return JsonResponse(data)

    def form_valid(self, form):
        category = form.save(commit=False)
        messages.success(self.request, 'Kategori med navnet: ' + category.category_title + " ble opprettet.")
        return super(CategoryCreateView, self).form_valid(form)


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
        inputfield = []
        task_id = request.GET['task_id']
        task = Task.objects.get(id=task_id)
        data = {
            'task_title': task.title,
            'task_text': task.text,
            'answer_text': task.answerText,
            'task_reasoning': task.reasoning,
            'task_reasoningText': task.reasoningText,
            'task_extra': task.extra,
            'task_answertype': task.answertype,
            'options': multiplechoice,
            'inputfields': inputfield
        }
        if task.extra == 1:
            geogebra = GeogebraTask.objects.get(task_id=task_id)
            data['geogebra_preview'] = geogebra.preview
        elif task.extra == 2:
            image_task = ImageTask.objects.get(task_id=task_id)
            path = image_task.image.url
            data['path'] = path
        if task.answertype == 2:
            multiplechoice_task = MultipleChoiceTask.objects.filter(task_id=task_id)
            for choices in multiplechoice_task:
                options = []
                multiple_choice_options = MultipleChoiceOption.objects.filter(MutipleChoiceTask=choices)
                for option in multiple_choice_options:
                    options.append(option.option)
                multiplechoice.append({
                    'question': choices.question,
                    'checkbox': choices.checkbox,
                    'options': options
                })
        elif task.answertype == 4:
            inputfieldtasks = InputFieldTask.objects.filter(task=task)
            for inputfieldtask in inputfieldtasks:
                fields = []
                length = []
                fraction = []
                inputfields = InputField.objects.filter(inputFieldTask=inputfieldtask)
                for input in inputfields:
                    fields.append(input.title)
                    length.append(input.inputlength)
                    fraction.append(input.fraction)
                inputfield.append({
                    "question": inputfieldtask.question,
                    "fields": fields,
                    "length": length,
                    "fraction": fraction
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
        context['form'] = CreateTaskLog()
        return context


class TaskDetailView(AdministratorCheck, views.AjaxResponseMixin, generic.DetailView):
    """
        Class that displays information about a single task object based on the task_id.

        :func:`AdministratorCheck`:
            inherited permission check, checks if the logged in user is an administrator.
        **AjaxResponseMixin:**
            This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
        **DetailView:**
            Inherits generic.DetailView that makes a page representing a specific object.
    """
    template_name = 'maths/task_detail.html'
    model = Task
    pk_url_kwarg = 'task_pk'

    def get_ajax(self, request, *args, **kwargs):
        item_id = request.GET['item_id']
        item = Item.objects.get(id=item_id)
        data = {
            'description': item.task.variableDescription,
            'variables': item.variables
        }
        return JsonResponse(data)

    def post_ajax(self, request, *args, **kwargs):
        update_description = request.POST['updateDescription']
        if update_description in 'true':
            description = request.POST['description']
            task = Task.objects.get(id=self.kwargs.get('task_pk'))
            task.variableDescription = description
            task.save()
            data = {
                'id': task.id
            }
        else:
            variables = request.POST['variables']
            randomVariables = request.POST['randomVariables']
            if not Item.objects.filter(task_id=self.kwargs.get('task_pk'), variables=variables,
                                       random_variables=False).exists():
                item = Item(task_id=self.kwargs.get('task_pk'), variables=variables)
                if randomVariables == 'true':
                    item.random_variables = True
                item.save()
                data = {
                    'id': item.id
                }
            else:
                item = Item.objects.get(task_id=self.kwargs.get('task_pk'), variables=variables)
                data = {
                    'id': item.id
                }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        task_id = self.kwargs.get('task_pk')
        items = Item.objects.filter(task_id=task_id)
        geogebra = GeogebraTask.objects.get(task_id=task_id)
        context['items'] = items
        context['geogebra'] = geogebra
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
    success_url = reverse_lazy('maths:directoryRoot')

    def get_initial(self):
        """
        Function that checks for preset values and sets them to the fields.

        :return: List of the preset values.
        """
        task_pk = self.kwargs.get("task_pk")
        task = Task.objects.get(id=task_pk)
        data = {}
        if GeogebraTask.objects.filter(task_id=task_pk).exists():
            geo = GeogebraTask.objects.get(task=task)
            data['width'] = geo.width
            data['height'] = geo.height
            data['showMenuBar'] = geo.showMenuBar
            data['enableLabelDrags'] = geo.enableLabelDrags
            data['enableShiftDragZoom'] = geo.enableShiftDragZoom
            data['enableRightClick'] = geo.enableRightClick
        return data

    def get_context_data(self, **kwargs):
        """
            Function that adds the multiple choice options and geogebra to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        if GeogebraTask.objects.filter(task=self.kwargs.get("task_pk")).exists():
            context['geogebra'] = GeogebraTask.objects.get(task=self.kwargs.get("task_pk"))
        if MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk")):
            context['options'] = MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk"))
        if ImageTask.objects.filter(task_id=self.kwargs.get('task_pk')).exists():
            context['image'] = ImageTask.objects.get(task_id=self.kwargs.get('task_pk'))

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
        self.success_url = reverse_lazy('maths:directoryDetail', kwargs={
            'directory_pk': task.directory.id
        })
        if self.request.POST.get('create_new', False):
            task.pk = None
            task.save()
            item = Item(task=task)
            item.save()
        else:
            task.save()
        if task.extra == 1:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            showMenuBar = form.cleaned_data['showMenuBar']
            enableLabelDrags = form.cleaned_data['enableLabelDrags']
            enableShiftDragZoom = form.cleaned_data['enableShiftDragZoom']
            enableRightClick = form.cleaned_data['enableRightClick']
            algebraInputField = form.cleaned_data['algebraInputField']
            xmin = form.cleaned_data['xmin']
            xmax = form.cleaned_data['xmax']
            ymin = form.cleaned_data['ymin']
            ymax = form.cleaned_data['ymax']
            yratio = form.cleaned_data['yratio']
            xstep = form.cleaned_data['xstep']
            ystep = form.cleaned_data['ystep']
            geotask = GeogebraTask.objects.filter(task=task)
            if geotask.count() > 0:
                geogebratask = GeogebraTask.objects.get(task=task)
                geogebratask.base64 = base64
                geogebratask.preview = preview
                geogebratask.showMenuBar = showMenuBar
                geogebratask.enableLabelDrags = enableLabelDrags
                geogebratask.enableShiftDragZoom = enableShiftDragZoom
                geogebratask.enableRightClick = enableRightClick
                geogebratask.algebraInputField = algebraInputField
                geogebratask.xmin = xmin
                geogebratask.xmax = xmax
                geogebratask.ymin = ymin
                geogebratask.ymax = ymax
                geogebratask.yratio = yratio
                geogebratask.xstep = xstep
                geogebratask.ystep = ystep
                geogebratask.save()
            else:
                height = form.cleaned_data['height']
                width = form.cleaned_data['width']
                geogebratask = GeogebraTask(task=task, base64=base64, preview=preview, height=height, width=width,
                                            xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, yratio=yratio, xstep=xstep,
                                            ystep=ystep, showMenuBar=showMenuBar, enableLabelDrags=enableLabelDrags,
                                            enableShiftDragZoom=enableShiftDragZoom, enableRightClick=enableRightClick,
                                            algebraInputField=algebraInputField)
                geogebratask.save()
        if task.answertype == 2:
            taskoptions = MultipleChoiceTask.objects.filter(task=task)
            taskoptions.delete()
            options = self.request.POST['options']
            correct = self.request.POST['correct']
            questions = self.request.POST['questions']
            radio_or_check = self.request.POST['radioOrCheck']
            option_split = options.split('<--->')
            correct_split = correct.split('<--->')
            question_split = questions.split('|||||')
            radio_or_check_split = radio_or_check.split('|||||')
            x = 0
            for question in question_split:
                multiple_choice_task = MultipleChoiceTask(question=question, task=task)
                if radio_or_check_split[x] == 'true':
                    multiple_choice_task.checkbox = True
                else:
                    multiple_choice_task.checkbox = False
                multiple_choice_task.save()
                multiple_choice_options = option_split[0].split('|||||')
                multiple_choice_options_correct = correct_split[0].split('|||||')
                for i in range(0, len(multiple_choice_options)):
                    multiple_choice_option = MultipleChoiceOption(MutipleChoiceTask=multiple_choice_task,
                                                                  option=multiple_choice_options[i])
                    if multiple_choice_options_correct[i] == 'true':
                        multiple_choice_option.correct = True
                    else:
                        multiple_choice_option.correct = False
                    multiple_choice_option.save()
                option_split.pop(0)
                correct_split.pop(0)
                x += 1
        elif task.answertype == 4:
            created_inputs = InputFieldTask.objects.filter(task=task)
            created_inputs.delete()
            input_questions = form.cleaned_data['inputQuestion']
            inputfield = form.cleaned_data['inputField']
            inputlength = form.cleaned_data['inputLength']
            inputcorrect = form.cleaned_data['inputCorrect']
            inputfraction = form.cleaned_data['inputFraction']
            inputfield_split = inputfield.split('<--->')
            inputlength_split = inputlength.split('<--->')
            inputcorrect_split = inputcorrect.split('<--->')
            inputfraction_split = inputfraction.split('<--->')
            input_questions_split = input_questions.split('|||||')
            x = 1
            for i in range(0, len(input_questions_split)):
                inputfieldtask = InputFieldTask(task=task, question=input_questions_split[i])
                inputfieldtask.save()
                inputfields = inputfield_split[i].split('|||||')
                input_length = inputlength_split[i].split('|||||')
                input_correct = inputcorrect_split[i].split('|||||')
                input_fraction = inputfraction_split[i].split('|||||')
                for y in range(0, len(inputfields)):
                    input = InputField(inputFieldTask=inputfieldtask, title=inputfields[y], inputnr=x,
                                       inputlength=input_length[y])
                    if input_correct[y]:
                        input.correct = input_correct[y]
                    if input_fraction[y] == "1":
                        input.fraction = True
                    input.save()
                    x += 1
        return super(TaskUpdateView, self).form_valid(form)


class TaskCollectionCreateView(AdministratorCheck, views.AjaxResponseMixin, generic.CreateView):
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
    fields = ['test_name', 'items']

    def get_ajax(self, request, *args, **kwargs):
        ids = []
        variables = []
        id = request.GET['id']
        items = Item.objects.filter(task_id=id)
        for item in items:
            ids.append(item.id)
            variables.append(item.variables)
        data = {
            'ids': ids,
            'variables': variables,
            'description': item.task.variableDescription,
            'variableTask': item.task.variableTask
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all the task and category objects to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionCreateView, self).get_context_data(**kwargs)
        directory = Directory.objects.get(parent_directory=None)
        context['directory'] = directory
        context['sub_directories'] = Directory.objects.filter(parent_directory=directory)
        context['tasks'] = Task.objects.all()
        context['categories'] = Category.objects.all()
        context['update'] = False
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
            if group.grade:
                grade = group.grade.school.school_name + " - " + group.grade.grade_name
            else:
                grade = "-"
            groups.append({
                'group_name': group.group_name,
                'grade': grade,
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
        context['update'] = Answer.objects.filter(
            test__task_collection_id=self.kwargs.get('taskCollection_pk')).exists()
        return context


class TaskCollectionUpdateView(AdministratorCheck, views.AjaxResponseMixin, generic.UpdateView):
    template_name = 'maths/taskCollection_form.html'
    model = TaskCollection
    fields = ['test_name', 'items']
    pk_url_kwarg = 'taskCollection_pk'

    def get_ajax(self, request, *args, **kwargs):
        item_id = request.GET['id']
        item = Item.objects.get(id=item_id)
        data = {
            'id': item.task.id
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all the task and category objects to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionUpdateView, self).get_context_data(**kwargs)
        directory = Directory.objects.get(parent_directory=None)
        context['directory'] = directory
        context['sub_directories'] = Directory.objects.filter(parent_directory=directory)
        context['tasks'] = Task.objects.all()
        context['categories'] = Category.objects.all()
        context['update'] = True
        return context


class TaskCollectionDeleteView(AdministratorCheck, generic.DeleteView):
    model = TaskCollection
    pk_url_kwarg = 'taskCollection_pk'
    success_url = reverse_lazy('maths:taskCollectionList')

    def delete(self, request, *args, **kwargs):
        task_collection = TaskCollection.objects.get(id=self.kwargs.get('taskCollection_pk'))
        success_message = 'Testen "' + task_collection.test_name + '" ble slettet.'
        messages.success(self.request, success_message)
        return super(TaskCollectionDeleteView, self).delete(request, *args, **kwargs)


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
                taskorder = TaskOrder(test=test, item_id=order)
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

    def post_ajax(self, request, *args, **kwargs):
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        public = request.POST['public']
        if public == 'true':
            test.public = True
        else:
            test.public = False
        test.save()
        data = {
            'success': True
        }
        return JsonResponse(data)

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
            context['anonymous_answers'] = TestAnswer.objects.filter(test=test, user__isnull=True, status=3).order_by('-id')
        return context


class AnswerCreateView2(AnswerCheck, views.AjaxResponseMixin, generic.FormView):
    template_name = 'maths/answer_form2.html'
    form_class = CreateTestAnswerForm

    def get_success_url(self):
        """
            Function that returns the success url.
            :return: success url.
        """
        if Person.objects.filter(id=self.request.user.id).exists():
            return reverse_lazy('maths:index')
        else:
            return reverse_lazy('maths:answerFinished')

    def form_valid(self, form):
        data = form.cleaned_data
        test_answer = TestAnswer.objects.get(id=data['testAnswer_id'])
        test_answer.status = 3
        test_answer.save()
        return super(AnswerCreateView2, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AnswerCreateView2, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        context['test_id'] = test.id
        context['test_name'] = test.task_collection.test_name
        context['test_strict'] = test.strictOrder
        geogebra = False
        for item in test.task_collection.items.all():
            if GeogebraTask.objects.filter(task=item.task).exists():
                geogebra = True
        context['geogebra'] = geogebra
        if test.randomOrder:
            randomtest = sorted(test.task_collection.items.only('id').all(), key=lambda x: random.random())
            context['items'] = randomtest
            item = Item.objects.get(id=randomtest[0].id)
            context['item'] = item
        else:
            taskorder = TaskOrder.objects.filter(test=test)
            context['items'] = Item.objects.filter(taskorder__in=taskorder).only('id')
            item = Item.objects.get(id=context['items'][0].id)
            context['item'] = item
        if not self.request.user.is_anonymous():
            if self.request.user.role == 1:
                if TestAnswer.objects.filter(test=test, user=self.request.user).exists():
                    test_answer_id = TestAnswer.objects.get(test=test, user=self.request.user).id
                else:
                    test_answer = TestAnswer(test=test, user=self.request.user)
                    test_answer.save()
                    test_answer_id = test_answer.id
                context['testanswer'] = test_answer_id
                if Answer.objects.filter(item=item, testAnswer_id=test_answer_id).exists():
                    answer = Answer.objects.get(item=item, testAnswer_id=test_answer_id)
                    context['answer_id'] = answer.id
                    context['answer_text'] = answer.text
                    context['answer_reasoning'] = answer.reasoning
        else:
            test_answer = TestAnswer(test=test)
            s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
            passlen = 12
            anonymous_user_string_found = False
            while not anonymous_user_string_found:
                anonymous_user_string = "".join(random.sample(s, passlen))
                if not TestAnswer.objects.filter(anonymous_user=anonymous_user_string).exists():
                    anonymous_user_string_found = True
            print(anonymous_user_string)
            test_answer.anonymous_user = anonymous_user_string
            test_answer.save()
            test_answer_id = test_answer.id
        if test_answer_id:
            context['testanswer'] = test_answer_id
        else:
            context['testanswer'] = -1
        return context

    def post_ajax(self, request, *args, **kwargs):
        testanswer_id = request.POST.get('testanswer')
        item_id = request.POST.get('item')
        answer_text = request.POST.get('text')
        reasoning = request.POST.get('reasoning')
        timespent = request.POST.get('timespent')
        correct = request.POST.get('correct')
        data = {}
        if Answer.objects.filter(testAnswer_id=testanswer_id, item_id=item_id).exists():
            answer = Answer.objects.get(testAnswer__id=testanswer_id, item_id=item_id)
            data['answer_id'] = answer.id
            answer.timespent = answer.timespent + "|||||" + timespent
            if answer_text:
                if answer_text == "-":
                    answer.text = ""
                else:
                    answer.text = answer_text
                if answer.item.task.answertype == 4:
                    input_answers = answer_text.split('|||||')
                    inputfield_tasks = InputFieldTask.objects.filter(task=answer.item.task)
                    x = 0
                    score = 0
                    score_tasks = False
                    for inputfield_task in inputfield_tasks:
                        inputfields = InputField.objects.filter(inputFieldTask=inputfield_task)
                        for inputfield in inputfields:
                            if inputfield.correct:
                                input_answer = input_answers[x].strip()
                                score_tasks = True
                                if input_answer:
                                    if float(input_answer) == float(inputfield.correct):
                                        score += 1
                            x += 1
                    if score_tasks:
                        answer.correct = score
                elif answer.item.task.answertype == 2:
                    score = 0
                    multiplechoice_answer = answer_text.split('<--|-->')
                    count = 0
                    for multiplechoicetask in answer.item.task.multiplechoicetask_set.all():
                        correct_string = ""
                        for option in multiplechoicetask.multiplechoiceoption_set.all():
                            if option.correct:
                                correct_string += option.option + '|||||'
                        correct_string = correct_string[:-5]
                        if multiplechoice_answer[count] == correct_string:
                            score += 1
                        count += 1
                    answer.correct = score
            if correct:
                answer.correct = correct
            if reasoning:
                answer.reasoning = reasoning
            base64 = request.POST.get("base64answer")
            answer.date_answered = timezone.now()
            answer.save()
            if base64:
                geogebra_answer = GeogebraAnswer.objects.get(answer=answer)
                geogebra_answer.base64 = base64
                geogebra_answer.matistikkAnswer = request.POST.get('matistikkAnswer')
                geogebra_answer.xmin = request.POST.get('xmin')
                geogebra_answer.xmax = request.POST.get('xmax')
                geogebra_answer.ymin = request.POST.get('ymin')
                geogebra_answer.ymax = request.POST.get('ymax')
                geogebra_answer.ratio = request.POST.get('yratio')
                geogebra_answer.save()
        else:
            answer = Answer(text=answer_text, reasoning=reasoning, testAnswer_id=testanswer_id,
                            timespent=timespent)
            answer.date_answered = timezone.now()
            # Fjern dette ved oppdatering
            answer.test_id = self.kwargs.get('test_pk')
            # -------------------------------------------------
            item = Item.objects.get(id=item_id)
            if item.random_variables:
                variables = request.POST['variables']
                obj, created = Item.objects.get_or_create(task=item.task, variables=variables, random_variables=False)
                answer.item = obj
            else:
                answer.item = item
            if correct:
                answer.correct = correct
            elif answer.item.task.answertype == 4:
                input_answers = answer_text.split('|||||')
                inputfield_tasks = InputFieldTask.objects.filter(task=answer.item.task)
                x = 0
                score = 0
                score_tasks = False
                for inputfield_task in inputfield_tasks:
                    inputfields = InputField.objects.filter(inputFieldTask=inputfield_task)
                    for inputfield in inputfields:
                        if inputfield.correct:
                            input_answer = input_answers[x].strip()
                            score_tasks = True
                            if input_answer:
                                if float(input_answer) == float(inputfield.correct):
                                    score += 1
                        x += 1
                if score_tasks:
                    answer.correct = score
            elif answer.item.task.answertype == 2:
                score = 0
                multiplechoice_answer = answer_text.split('<--|-->')
                count = 0
                for multiplechoicetask in answer.item.task.multiplechoicetask_set.all():
                    correct_string = ""
                    for option in multiplechoicetask.multiplechoiceoption_set.all():
                        if option.correct:
                            correct_string += option.option + '|||||'
                    correct_string = correct_string[:-5]
                    if multiplechoice_answer[count] == correct_string:
                        score += 1
                    count += 1
                answer.correct = score
            answer.date_answered = timezone.now()
            answer.save()
            if item.task.extra == 1:
                base64 = request.POST.get("base64answer")
                matistikkAnswer = request.POST.get('matistikkAnswer')
                xmin = request.POST.get('xmin')
                xmax = request.POST.get('xmax')
                ymin = request.POST.get('ymin')
                ymax = request.POST.get('ymax')
                ratio = request.POST.get('yratio')
                # geogebra_data = request.POST["task" + str(y) + "-geogebradata"]
                geogebra_answer = GeogebraAnswer(answer=answer, base64=base64,
                                                 matistikkAnswer=matistikkAnswer, yratio=ratio, xmin=xmin, xmax=xmax,
                                                 ymin=ymin, ymax=ymax)
                geogebra_answer.save()
            data['answer_id'] = answer.id
        return JsonResponse(data=data)

    def get_ajax(self, request, *args, **kwargs):
        item_id = request.GET.get('itemid')
        testAnswer_id = request.GET.get('testAnswer')
        data = {}
        if item_id == "0":
            answers = Answer.objects.filter(testAnswer_id=testAnswer_id)
            answer_tab = []
            for answer in answers:
                answer_data = {
                    'id': answer.item.id
                }
                answer_text = answer.text.strip("|").strip('<--|-->')
                print(answer_text)
                if answer.item.task.answertype == 3 or answer_text:
                    answer_data['status'] = 'Besvart'
                else:
                    answer_data['status'] = 'Tom besvarelse'
                if answer.item.task.reasoning:
                    if not answer.reasoning:
                        answer_data['status'] += " | Tom begrunnelse"
                        print('tomt')
                answer_tab.append(answer_data)
            data['states'] = answer_tab
        else:
            item = Item.objects.get(id=item_id)
            data['tasktext'] = item.task.text
            data['extra'] = item.task.extra
            data['answertype'] = item.task.answertype
            data['reasoning'] = item.task.reasoning
            data['reasoningtext'] = item.task.reasoningText
            if item.task.answertype == 1:
                data['answertext'] = item.task.answerText
            elif item.task.answertype == 2:
                multiplechoicetasks = MultipleChoiceTask.objects.filter(task=item.task)
                multiplechoicedata = []
                for multiplechoicetask in multiplechoicetasks:
                    options = ""
                    multiplechoicetaskdata = {
                        "question": multiplechoicetask.question,
                        "checkbox": multiplechoicetask.checkbox
                    }
                    length = 0
                    for option in multiplechoicetask.multiplechoiceoption_set.all():
                        options += option.option + "|||||"
                        length += len(option.option)
                    options = options[:-5]
                    multiplechoicetaskdata['options'] = options
                    multiplechoicetaskdata['length'] = length
                    multiplechoicedata.append(multiplechoicetaskdata)
                data['multiplechoice'] = multiplechoicedata
            elif item.task.answertype == 4:
                inputfielddata = []
                inputfieldtasks = InputFieldTask.objects.filter(task=item.task)
                for inputfieldtask in inputfieldtasks:
                    inputfieldtaskdata = {
                        'question': inputfieldtask.question
                    }
                    fields = []
                    for field in inputfieldtask.inputfield_set.all():
                        fielddata = {
                            "inputtitle": field.title,
                            "inputlength": field.inputlength,
                            "inputnr": field.inputnr
                        }
                        fields.append(fielddata)
                    inputfieldtaskdata['inputfields'] = fields
                    inputfielddata.append(inputfieldtaskdata)
                data['inputfields'] = inputfielddata
            if item.task.extra == 1:
                geogebra_task = GeogebraTask.objects.get(task=item.task)
                data['base64'] = geogebra_task.base64
                data['xmin'] = geogebra_task.xmin
                data['xmax'] = geogebra_task.xmax
                data['ymin'] = geogebra_task.ymin
                data['ymax'] = geogebra_task.ymax
                data['yratio'] = geogebra_task.yratio
                data['xstep'] = geogebra_task.xstep
                data['ystep'] = geogebra_task.ystep
                data['showMenuBar'] = geogebra_task.showMenuBar
                data['algebraInputField'] = geogebra_task.algebraInputField
                data['enableLabelDrags'] = geogebra_task.enableLabelDrags
                data['enableShiftDragZoom'] = geogebra_task.enableShiftDragZoom
                data['enableRightClick'] = geogebra_task.enableRightClick
            elif item.task.extra == 2:
                image_task = ImageTask.objects.get(task=item.task)
                data['image'] = image_task.image.url
            if int(testAnswer_id) > 0:
                if Answer.objects.filter(item_id=item_id, testAnswer_id=testAnswer_id).exists():
                    answer = Answer.objects.get(item_id=item_id, testAnswer_id=testAnswer_id)
                    data['answer_id'] = answer.id
                    data['prev_answer'] = answer.text
                    if answer.item.task.reasoning:
                        data['prev_reasoning'] = answer.reasoning
                    if answer.item.task.extra == 1:
                        geogebra_answer = GeogebraAnswer.objects.get(answer=answer)
                        data['base64'] = geogebra_answer.base64
                        data['xmin'] = geogebra_answer.xmin
                        data['xmax'] = geogebra_answer.xmax
                        data['ymin'] = geogebra_answer.ymin
                        data['ymax'] = geogebra_answer.ymax
                        data['yratio'] = geogebra_answer.yratio
        return JsonResponse(data)


class AnswerCreateView(AnswerCheck, views.AjaxResponseMixin, generic.FormView):
    """
   Class for creating answers for all the tasks in a test.

    :func:`AnswerCheck`:
        inherited permission check, checks if the logged in user can answer the test.
    **FormView**
       A view that displays a form.
    """
    form_class = CreateAnswerForm
    template_name = 'maths/answer_form.html'

    def post_ajax(self, request, *args, **kwargs):
        test_id = self.kwargs.get('test_pk')
        item_id = request.POST["itemid"]
        answer_text = request.POST['answer']
        reasoning = request.POST['reasoning']
        correct = request.POST['correct']
        timespent = request.POST['timespent']
        anonymous_user_id = request.POST['anonymous_user_id']
        answer = Answer(test_id=test_id, text=answer_text, reasoning=reasoning, timespent=timespent)
        item = Item.objects.get(id=item_id)
        if item.random_variables:
            variables = request.POST['variables']
            obj, created = Item.objects.get_or_create(task=item.task, variables=variables, random_variables=False)
            answer.item = obj
        else:
            answer.item = item
        if correct:
            answer.correct = correct
        elif answer.item.task.answertype == 4:
            input_answers = answer_text.split('|||||')
            inputfield_tasks = InputFieldTask.objects.filter(task=answer.item.task)
            x = 0
            score = 0
            score_tasks = False
            for inputfield_task in inputfield_tasks:
                inputfields = InputField.objects.filter(inputFieldTask=inputfield_task)
                for inputfield in inputfields:
                    if inputfield.correct:
                        input_answer = input_answers[x].strip()
                        score_tasks = True
                        if input_answer:
                            if float(input_answer) == float(inputfield.correct):
                                score += 1
                    x += 1
            if score_tasks:
                answer.correct = score
        if answer.item.task.answertype == 2:
            score = 0
            multiplechoice_answer = answer_text.split('<--|-->')
            count = 0
            for multiplechoicetask in answer.item.task.multiplechoicetask_set.all():
                correct_string = ""
                for option in multiplechoicetask.multiplechoiceoption_set.all():
                    if option.correct:
                        correct_string += option.option + '|||||'
                correct_string = correct_string[:-5]
                if multiplechoice_answer[count] == correct_string:
                    score += 1
                count += 1
            answer.correct = score
        answer.date_answered = timezone.now()
        if Person.objects.filter(id=self.request.user.id).exists():
            answer.user = self.request.user
        else:
            answer.user = None
            if not anonymous_user_id:
                answerList = Answer.objects.filter(user__isnull=True).last()
                if answerList:
                    anonymous_user_id = int(answerList.anonymous_user + 1)
                    answer.anonymous_user = anonymous_user_id
                else:
                    answer.anonymous_user = 0
            else:
                answer.anonymous_user = anonymous_user_id
        answer.save()
        if item.task.extra == 1:
            base64 = request.POST["base64"]
            matistikkAnswer = request.POST['matistikkAnswer']
            xmin = request.POST['xmin']
            xmax = request.POST['xmax']
            ymin = request.POST['ymin']
            ymax = request.POST['ymax']
            ratio = request.POST['ratio']
            # geogebra_data = request.POST["task" + str(y) + "-geogebradata"]
            geogebra_answer = GeogebraAnswer(answer=answer, base64=base64,
                                             matistikkAnswer=matistikkAnswer, yratio=ratio, xmin=xmin, xmax=xmax,
                                             ymin=ymin, ymax=ymax)
            # geogebra_answer.save()
        data = {
            'anonymous_user_id': anonymous_user_id
        }
        return JsonResponse(data)

    def get_success_url(self):
        """
            Function that returns the success url.
            :return: success url.
        """
        if Person.objects.filter(id=self.request.user.id).exists():
            return reverse_lazy('maths:index')
        else:
            return reverse_lazy('maths:answerFinished')

    def get_context_data(self, **kwargs):
        """
            Function that adds all information needed about a specific test and adds a form for each task in the test
            without overriding it. 

            :param kwargs: Keyword arguments
            :return: Updated context
        """
        context = super(AnswerCreateView, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        context['test'] = test
        """
        Henter ut tilfedlige variable fra en annen server.
        data = {
            'variables': 3,
        }
        r = requests.get('http://127.0.0.1:8005/', params=data)
        json_data = json.loads(r.text)
        """
        if test.randomOrder:
            randomtest = sorted(test.task_collection.items.all(), key=lambda x: random.random())
            context['items'] = randomtest
        else:
            task_order = TaskOrder.objects.filter(test=test)
            context['items'] = Item.objects.filter(taskorder__in=task_order)
        forms = []
        for z in range(0, len(test.task_collection.items.all())):
            forms.append(CreateAnswerForm(prefix="task" + str(z)))
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
        answerList = Answer.objects.filter(user__isnull=True).last()
        for y in range(0, len(test.task_collection.items.all())):
            text = request.POST["task" + str(y) + "-text"]
            reasoning = request.POST["task" + str(y) + "-reasoning"]
            itemid = request.POST["task" + str(y) + "-item"]
            timespent = request.POST["task" + str(y) + "-timespent"]
            correct = request.POST["task" + str(y) + "-correct"]
            answer = Answer(text=text, reasoning=reasoning, test=test,
                            timespent=timespent)
            if Person.objects.filter(id=self.request.user.id).exists():
                answer.user = self.request.user
                url = reverse('maths:index')
            else:
                url = reverse('maths:answerFinished')
                answer.user = None
                if answerList:
                    answer.anonymous_user = int(answerList.anonymous_user + 1)
                else:
                    answer.anonymous_user = 0
            item = Item.objects.get(id=itemid)
            if item.random_variables:
                variables = request.POST['task' + str(y) + "-variables"]
                obj, created = Item.objects.get_or_create(task=item.task, variables=variables, random_variables=False)
                answer.item = obj
            else:
                answer.item = item
            if correct:
                answer.correct = correct
            elif answer.item.task.answertype == 4:
                input_answers = text.split('|||||')
                inputfield_tasks = InputFieldTask.objects.filter(task=answer.item.task)
                x = 0
                score = 0
                score_tasks = False
                for inputfield_task in inputfield_tasks:
                    inputfields = InputField.objects.filter(inputFieldTask=inputfield_task)
                    for inputfield in inputfields:
                        if inputfield.correct:
                            input_answer = input_answers[x].strip()
                            score_tasks = True
                            if input_answer:
                                if float(input_answer) == float(inputfield.correct):
                                    score += 1
                        x += 1
                if score_tasks:
                    answer.correct = score
            if answer.item.task.answertype == 2:
                score = 0
                multiplechoice_answer = text.split('<--|-->')
                count = 0
                for multiplechoicetask in answer.item.task.multiplechoicetask_set.all():
                    correct_string = ""
                    for option in multiplechoicetask.multiplechoiceoption_set.all():
                        if option.correct:
                            correct_string += option.option + '|||||'
                    correct_string = correct_string[:-5]
                    if multiplechoice_answer[count] == correct_string:
                        score += 1
                    count += 1
                answer.correct = score
            answer.date_answered = timezone.now()
            answer.save()
            base64 = request.POST["task" + str(y) + "-base64answer"]
            geogebradata = request.POST["task" + str(y) + "-geogebradata"]
            matistikkAnswer = request.POST["task" + str(y) + "-matistikkAnswer"]
            if item.task.extra == 1:
                geogebraanswer = GeogebraAnswer(answer=answer, base64=base64, data=geogebradata,
                                                matistikkAnswer=matistikkAnswer)
                geogebraanswer.save()
        success_message = 'Dine svar ble levert!'
        messages.success(self.request, success_message)
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
    template_name = 'maths/test_list.html'

    def get_queryset(self):
        return Test.objects.filter(person=self.request.user)

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
        grades = Grade.objects.filter(person=self.request.user)
        context['grades'] = grades
        context['students'] = Person.objects.filter(grades__in=grades).distinct()
        if self.kwargs.get('test_pk'):
            context['modal'] = self.kwargs.get('test_pk')
        return context


class TestDeleteView(AdministratorCheck, generic.DeleteView):
    model = Test
    pk_url_kwarg = 'test_pk'
    success_message = "Den publiserte testen ble slettet."

    def get_success_url(self):
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        return reverse_lazy('maths:taskCollectionDetail', kwargs={
            'taskCollection_pk': test.task_collection.id
        })

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TestDeleteView, self).delete(request, *args, **kwargs)


class AnswerListView(AnswerCheck, generic.ListView):
    """
    Class that displays a list of answers for all the tasks in a specific test for a specific user.

    :func:`AnswerCheck`:
        inherited permission check, checks if the logged in user can answer the test.
    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    template_name = 'maths/answer_list.html'

    def get_queryset(self):
        """
            Function that sets the query for getting the object_list. 
            
            :return: List of answer objects.
        """
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        if self.kwargs.get('slug'):
            person = Person.objects.get(username=self.kwargs.get('slug'))
            return Answer.objects.filter(test=test, user=person)
        else:
            anonymous_user = self.kwargs.get('user_id')
            return Answer.objects.filter(test=test, anonymous_user=anonymous_user)

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
        column_names = ['item_id', 'user_id', 'text', 'reasoning', 'timespent', 'date_answered']
        return excel.make_response_from_query_sets(answers, column_names, 'xlsx',
                                                   file_name=test.task_collection.test_name)
    else:
        array = ['#hackerman']
        return excel.make_response_from_array(array, 'xlsx', file_name='fasit')


class LinkSuccess(generic.TemplateView):
    template_name = 'maths/link_success.html'


class ExportData(AdministratorCheck, views.AjaxResponseMixin, generic.TemplateView):
    template_name = 'maths/export_view.html'

    def get_ajax(self, request, *args, **kwargs):
        data = []
        info_js = request.GET.get('info')
        rq_students = request.GET.get('students')
        rq_grades = request.GET.get('grades')
        rq_groups = request.GET.get('groups')
        rq_tests = request.GET.get('tests')
        rq_tasks = request.GET.get('tasks')
        rq_items = request.GET.get('items')
        if info_js == 'false':
            if rq_students:
                student_table = rq_students.split(',')
                for student in student_table:
                    user = Person.objects.get(username=student)
                    answers = Answer.objects.filter(user=user).order_by('-id')
                    for answer in answers:
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        answer_tab = [user.username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
            if rq_grades:
                grade_table = rq_grades.split(',')
                for grade_id in grade_table:
                    grade = Grade.objects.get(id=grade_id)
                    tests = Test.objects.filter(grade=grade)
                    answers = Answer.objects.filter(test__in=tests, user__in=grade.person_set.all())
                    for answer in answers:
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        answer_tab = [answer.user.username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
            if rq_groups:
                group_table = rq_groups.split(',')
                for group_id in group_table:
                    group = Gruppe.objects.get(id=group_id)
                    tests = Test.objects.filter(gruppe=group)
                    answers = Answer.objects.filter(test__in=tests, user__in=group.persons.all()).order_by('-id')
                    for answer in answers:
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        answer_tab = [answer.user.username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
            if rq_tests:
                test_table = rq_tests.split(',')
                for test_id in test_table:
                    test = Test.objects.get(id=test_id)
                    answers = Answer.objects.filter(test=test).order_by('-id')
                    for answer in answers:
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        if answer.user:
                            username = answer.user.username
                        else:
                            username = "Anonym  - " + str(answer.anonymous_user)
                        answer_tab = [username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
            if rq_tasks:
                task_table = rq_tasks.split(',')
                for task_id in task_table:
                    task = Task.objects.get(id=task_id)
                    answers = Answer.objects.filter(item__task=task).order_by('-id')
                    for answer in answers:
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        if answer.user:
                            username = answer.user.username
                        else:
                            username = "Anonym  - " + str(answer.anonymous_user)
                        answer_tab = [username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
            if rq_items:
                item_table = rq_items.split(',')
                for item_id in item_table:
                    item = Item.objects.get(id=item_id)
                    answers = Answer.objects.filter(item=item).order_by('-id')
                    for answer in answers:
                        date_answered = formats.date_format(timezone.localtime(answer.date_answered),
                                                            "SHORT_DATETIME_FORMAT")
                        if GeogebraAnswer.objects.filter(answer=answer).exists():
                            geogebraAnswer = GeogebraAnswer.objects.get(answer=answer)
                            geogebra_data = geogebraAnswer.data
                            matistikk_answer = geogebraAnswer.matistikkAnswer
                        else:
                            geogebra_data = ""
                            matistikk_answer = ""
                        if answer.user:
                            username = answer.user.username
                        else:
                            username = "Anonym  - " + str(answer.anonymous_user)
                        answer_tab = [username, answer.test.__str__(), answer.item.__str__(), answer.text,
                                      answer.reasoning, answer.timespent, answer.correct, matistikk_answer,
                                      date_answered, geogebra_data]
                        data.append(answer_tab)
        elif info_js == 'true' and rq_students or rq_grades or rq_groups:
            if rq_students:
                student_table = rq_students.split(',')
                for student in student_table:
                    user = Person.objects.get(username=student)
                    grades = ""
                    groupsString = ""
                    for grade in user.grades.all():
                        grades += grade.__str__() + ", "
                    if user.role == 1:
                        role = 'Elev'
                        groups = Gruppe.objects.filter(persons=user)
                        for group in groups:
                            groupsString += group.__str__() + ", "
                    elif user.role == 2:
                        role = 'Lærer'
                    elif user.role == 3:
                        role = 'Skoleadministrator'
                        schools = School.objects.filter(school_administrator=user)
                        for school in schools:
                            grades += school.__str__() + ", "
                    else:
                        role = 'Administrator'
                    grades = grades[:-2]
                    groupsString = groupsString[:-2]
                    if user.last_login:
                        last_login = formats.date_format(timezone.localtime(user.last_login),
                                                         "SHORT_DATETIME_FORMAT")
                    else:
                        last_login = ""
                    answer_tab = [user.username, user.get_full_name(), user.date_of_birth, user.email, grades,
                                  groupsString, user.sex, role, last_login]
                    data.append(answer_tab)
            if rq_grades:
                grade_table = rq_grades.split(',')
                for grade_id in grade_table:
                    grade = Grade.objects.get(id=grade_id)
                    for user in grade.person_set.all():
                        grades = ""
                        groupsString = ""
                        for grade in user.grades.all():
                            grades += grade.__str__() + ", "
                        if user.role == 1:
                            role = 'Elev'
                            groups = Gruppe.objects.filter(persons=user)
                            for group in groups:
                                groupsString += group.__str__() + ", "
                        else:
                            role = 'Lærer'
                        grades = grades[:-2]
                        groupsString = groupsString[:-2]
                        if user.last_login:
                            last_login = formats.date_format(timezone.localtime(user.last_login),
                                                             "SHORT_DATETIME_FORMAT")
                        else:
                            last_login = ""
                        answer_tab = [user.username, user.get_full_name(), user.date_of_birth, user.email,
                                      grades, groupsString, user.sex, role, last_login]
                        data.append(answer_tab)
            if rq_groups:
                group_table = rq_groups.split(',')
                for group_id in group_table:
                    group = Gruppe.objects.get(id=group_id)
                    for user in group.persons.all():
                        grades = ""
                        groupsString = ""
                        for grade in user.grades.all():
                            grades += grade.__str__() + ", "
                        role = 'Elev'
                        for group in user.gruppe_set.all():
                            groupsString += group.__str__() + ", "
                        grades = grades[:-2]
                        groupsString = groupsString[:-2]
                        if user.last_login:
                            last_login = formats.date_format(timezone.localtime(user.last_login),
                                                             "SHORT_DATETIME_FORMAT")
                        else:
                            last_login = ""
                        answer_tab = [user.username, user.get_full_name(), user.date_of_birth, user.email,
                                      grades, groupsString, user.sex, role, last_login]
                        data.append(answer_tab)
        elif info_js == "true" and rq_tests:
            test_table = rq_tests.split(',')
            for test_id in test_table:
                test = Test.objects.get(id=test_id)
                order = ""
                items = ""
                for item in test.task_collection.items.all():
                    if item.variables:
                        items += item.task.title + " - (" + item.variables + "), "
                    else:
                        items += item.task.title + ", "
                items = items[:-2]
                if test.randomOrder:
                    order += "Fast og "
                else:
                    order += "Tilfeldig og "
                if test.strictOrder:
                    order += "Låst"
                else:
                    order += "Åpen"
                published = formats.date_format(timezone.localtime(test.published), "SHORT_DATETIME_FORMAT")
                if test.dueDate:
                    dueDate = formats.date_format(timezone.localtime(test.dueDate), "SHORT_DATETIME_FORMAT")
                else:
                    dueDate = ""
                answer_tab = [test.id, test.task_collection.test_name, published, dueDate, order,
                              test.task_collection.items.count(), items]
                data.append(answer_tab)
        elif info_js == 'true' and rq_tasks:
            task_table = rq_tasks.split(',')
            for task_id in task_table:
                task = Task.objects.get(id=task_id)
                answerfield = ""
                categories = ""
                variableTask = "Nei"
                variables = ""
                if task.answertype == 1:
                    answerfield += "Tekstsvar"
                elif task.answertype == 2:
                    answerfield += "Flervalg"
                else:
                    answerfield += "Kun tillegg"
                if task.reasoning:
                    answerfield += " og Begrunnelse"
                for category in task.category.all():
                    categories += category.__str__() + ", "
                if task.variableTask:
                    variableTask = "Ja"
                    for item in task.item_set.all():
                        variables += "(" + item.variables + "), "
                categories = categories[:-2]
                variables = variables[:-2]
                answer_tab = [task.id, task.title, task.text, answerfield, categories, variableTask, variables,
                              task.author.get_full_name()]
                data.append(answer_tab)
        else:
            item_table = rq_items.split(',')
            for item_id in item_table:
                item = Item.objects.get(id=item_id)
                answerfield = ""
                categories = ""
                tests_str = ""
                if item.task.answertype == 1:
                    answerfield += "Tekstsvar"
                elif item.task.answertype == 2:
                    answerfield += "Flervalg"
                else:
                    answerfield += "Kun tillegg"
                for category in item.task.category.all():
                    categories += category.__str__() + ", "
                categories = categories[:-2]
                for task_collection in item.taskcollection_set.all():
                    tests = Test.objects.filter(task_collection=task_collection)
                    for test in tests:
                        tests_str += test.__str__() + ", "
                tests_str = tests_str[:-2]
                answer_tab = [item.id, item.task.title, item.task.text, answerfield, categories, item.variables,
                              tests_str]
                data.append(answer_tab)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super(ExportData, self).get_context_data(**kwargs)
        context['students'] = Person.objects.filter(role=1)
        context['teachers'] = Person.objects.filter(role=2)
        context['schooladmins'] = Person.objects.filter(role=3)
        context['admins'] = Person.objects.filter(role=4)
        context['grades'] = Grade.objects.all()
        context['groups'] = Gruppe.objects.all()
        context['tests'] = Test.objects.all()
        context['tasks'] = Task.objects.all()
        context['items'] = Item.objects.all().order_by('-id')
        return context


class DirectoryDetailView(views.AjaxResponseMixin, generic.TemplateView):
    template_name = 'maths/directory_detail.html'

    def post_ajax(self, request, *args, **kwargs):
        directory_id = request.POST['id']
        name = request.POST['name']
        parent_id = request.POST['parent']
        if directory_id == "0":
            directory = Directory(name=name, author=request.user, date_created=timezone.now(),
                                  parent_directory_id=parent_id)
            directory.save()
        else:
            directory = Directory.objects.get(id=directory_id)
            directory.name = name
            directory.save()
        data = {
            "id": directory.id
        }
        return JsonResponse(data=data)

    def get_ajax(self, request, *args, **kwargs):
        directory_id = request.GET.get('directory')
        directory = Directory.objects.get(id=directory_id)
        sub_directories = Directory.objects.filter(parent_directory=directory)
        sub_directories_tab = []
        tasks_tab = []
        for sub_directory in sub_directories:
            sub_directory_data = {
                'id': sub_directory.id,
                'name': sub_directory.name
            }
            sub_directories_tab.append(sub_directory_data)
        tasks = Task.objects.filter(directory=directory)
        categories = Category.objects.filter(task__in=tasks).distinct()
        category_tab = []
        for category in categories:
            category_date = {
                'id': category.id,
                'name': category.category_title
            }
            category_tab.append(category_date)
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'author': task.author.username,
                'variableTask': task.variableTask,
                'approved': task.approved
            }
            category_str = ""
            for category in task.category.all():
                category_str += category.category_title + " - "
            category_str = category_str[:-3]
            task_data['categories'] = category_str
            tasks_tab.append(task_data)
        data = {
            'sub_directories': sub_directories_tab,
            'tasks': tasks_tab,
            'categories': category_tab
        }
        return JsonResponse(data=data)

    def get_context_data(self, **kwargs):
        context = super(DirectoryDetailView, self).get_context_data(**kwargs)
        if self.kwargs.get('directory_pk'):
            directory = Directory.objects.get(id=self.kwargs.get('directory_pk'))
            bread = []
            bread.insert(0, directory)
            parent = True
            if directory.parent_directory:
                parent_directory = directory.parent_directory
                while parent:
                    if parent_directory:
                        bread.insert(0, parent_directory)
                        parent_directory = parent_directory.parent_directory
                    else:
                        parent = False
            context['breadcrumbs'] = bread
        else:
            directory = Directory.objects.get(parent_directory=None)
        tasks = Task.objects.filter(directory=directory)
        context['directory'] = directory
        context['tasks'] = tasks
        context['sub_directories'] = Directory.objects.filter(parent_directory=directory)
        context['categories'] = Category.objects.filter(task__in=tasks).distinct()
        context['form'] = CreateTaskLog()
        return context


class DirectoryDelete(views.AjaxResponseMixin, generic.View):
    def post_ajax(self, request, *args, **kwargs):
        directory_id = request.POST['id']
        directory = Directory.objects.get(id=directory_id)
        parent_id = "0"
        if directory.parent_directory:
            parent_id = directory.parent_directory.id
        if Task.objects.filter(directory=directory).exists() or \
                Directory.objects.filter(parent_directory=directory).exists():
            return JsonResponse(data={
                'deleted': False
            })
        else:
            directory.delete()
        return JsonResponse(data={
            'deleted': True,
            'parent': parent_id
        })


class DirectoryEdit(views.AjaxResponseMixin, generic.View):
    def post_ajax(self, request, *args, **kwargs):
        directory_id = request.POST['id']
        new_name = request.POST['newName']
        directory = Directory.objects.get(id=directory_id)
        directory.name = new_name
        directory.save()
        return JsonResponse(data={
            'id': directory.id
        })


class DirectoryMove(views.AjaxResponseMixin, generic.View):
    def get_ajax(self, request, *args, **kwargs):
        get_root = request.GET.get('root')
        if get_root == "true":
            root = Directory.objects.get(parent_directory=None)
            directories = Directory.objects.filter(parent_directory=root)
            child_directories = []
            for directory in directories:
                children = Directory.objects.filter(parent_directory=directory)
                parent = children.exists()
                child_of_child = []
                for child in children:
                    parent_child = Directory.objects.filter(parent_directory=child).exists()
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'parent': parent_child
                    }
                    child_of_child.append(child_data)
                directory_data = {
                    'id': directory.id,
                    'name': directory.name,
                    'parent': parent,
                    'child': child_of_child
                }
                child_directories.append(directory_data)
            data = {
                "root_id": root.id,
                "root_name": root.name,
                "directories": child_directories
            }
            return JsonResponse(data)
        else:
            directory_id = request.GET.get('id')
            directories = Directory.objects.filter(parent_directory_id=directory_id)
            child_directories = []
            for directory in directories:
                children = Directory.objects.filter(parent_directory=directory)
                parent = children.exists()
                child_of_child = []
                for child in children:
                    parent_child = Directory.objects.filter(parent_directory=child).exists()
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'parent': parent_child
                    }
                    child_of_child.append(child_data)
                directory_data = {
                    'id': directory.id,
                    'name': directory.name,
                    'parent': parent,
                    'child': child_of_child
                }
                child_directories.append(directory_data)
            return JsonResponse(data={
                'directories': child_directories
            })

    def post_ajax(self, request, *args, **kwargs):
        destination_id = request.POST['destination']
        tasks_id = request.POST.get('tasks', False)
        directories_id = request.POST.get('directories', False)
        if tasks_id:
            task_tab = tasks_id.split(',')
            for task_id in task_tab:
                task = Task.objects.get(id=task_id)
                task.directory_id = destination_id
                task.save()
        if directories_id:
            directory_tab = directories_id.split(',')
            for directory_id in directory_tab:
                directory = Directory.objects.get(id=directory_id)
                directory.parent_directory_id = destination_id
                directory.save()
        destination = Directory.objects.get(id=destination_id)
        bread = []
        parent = True
        bread.insert(0, {
            'id': destination.id,
            'name': destination.name
        })
        if destination.parent_directory:
            parent_directory = destination.parent_directory
            while parent:
                if parent_directory:
                    parent_data = {
                        'id': parent_directory.id,
                        'name': parent_directory.name
                    }
                    bread.insert(0, parent_data)
                    parent_directory = parent_directory.parent_directory
                else:
                    parent = False
        return JsonResponse(data={
            'name': destination.name,
            'path': destination.__str__(),
            'breadcrumb': bread
        })


class TaskLogView(views.AjaxResponseMixin, generic.View):
    def get_ajax(self, request, *args, **kwargs):
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        taskLogs = TaskLog.objects.filter(task=task).order_by('-id')
        tasklog_list = []
        for tasklog in taskLogs:
            tasklog_dir = {
                'id': tasklog.id,
                'comment': tasklog.text,
                'author': tasklog.author.get_full_name(),
                'date': formats.date_format(timezone.localtime(tasklog.date), "SHORT_DATETIME_FORMAT"),
            }
            tasklog_list.append(tasklog_dir)
        return JsonResponse(data={
            'name': task.title,
            'logs': tasklog_list
        })

    def post_ajax(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id', False)
        text = request.POST.get('comment', False)
        approved = request.POST.get('approved', False)
        task = Task.objects.get(id=task_id)
        if text == 'approved':
            if approved == 'true':
                text = 'Oppgaven er satt som godkjent!'
                task.approved = True
            else:
                text = 'Oppgaven er satt som ikke godkjent!'
                task.approved = False
        taskLog = TaskLog(text=text, author=request.user, task=task, date=timezone.now())
        taskLog.save()
        task.save()
        return JsonResponse(data={
            'id': taskLog.id,
            'author': taskLog.author.get_full_name(),
            'comment': taskLog.text,
            'date': formats.date_format(timezone.localtime(taskLog.date), "SHORT_DATETIME_FORMAT"),
        })


class TaskLogDeleteView(views.AjaxResponseMixin, generic.View):
    def post_ajax(self, request, *args, **kwargs):
        log_id = request.POST.get('comment_id', False)
        log = TaskLog.objects.get(id=log_id)
        log.delete()
        return JsonResponse(data={
            'id': log_id
        })


class ItemDeleteView(AdministratorCheck, views.AjaxResponseMixin, generic.View):
    def post_ajax(self, request, *args, **kwargs):
        item_id = request.POST.get('id', False)
        item = Item.objects.get(id=item_id)
        if item.answer_set.exists() or item.task.item_set.count() < 2:
            return JsonResponse(data={
                'deleted': "False"
            })
        else:
            item.delete()
            return JsonResponse(data={
                'deleted': True
            })
