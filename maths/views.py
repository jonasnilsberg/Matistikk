from django.views import generic
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from .forms import CreateTaskForm
from .models import Task, MultipleChoiceTask, Category, GeogebraTask, TestBase


# Create your views here.


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


class CreateTaskView(generic.CreateView):
    """
    Class that creates a task.

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
            Function that adds all category objects to the context without overriding it.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(CreateTaskView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """
        Function that checks if the submitted :ref:`CreateTaskForm` is correct. If correct adds the logged in user as
        the author and creates the task with its extra information.

        :param form: References to the filled out model form.
        :return: calls super with the new form
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
            geogebratask = GeogebraTask(base64=base64, task=task)
            geogebratask.save()
        return super(CreateTaskView, self).form_valid(form)


class CategoryListView(generic.ListView):
    """
    Class that displays a template containing all category objects.

    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    model = Category
    template_name = 'maths/category_list.html'


class CategoryCreateView(generic.CreateView):
    """
    Class that creates a category.

    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    model = Category
    fields = ['category']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')


class CategoryUpdateView(generic.UpdateView):
    """
    Class that updates a category.

    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    model = Category
    fields = ['category']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')
    pk_url_kwarg = 'category_pk'


class TaskListView(generic.ListView):
    """
    Class that displays a template containing all task objects.

    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_list.html'
    model = Task

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class TaskUpdateView(generic.UpdateView):
    """
    Class that updates a task.

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
        task = form.save(commit=False)
        task.save()

        if task.extra:
            base64 = self.request.POST['base64']
            geotask = GeogebraTask.objects.filter(task=task)
            if geotask.count() > 0:
                geogebratask = GeogebraTask.objects.get(task=task)
                geogebratask.base64 = base64
                geogebratask.save()
            else:
                geogebratask = GeogebraTask(task=task, base64=base64)
                geogebratask.save()

        if task.answertype == 2:
            options = self.request.POST['options']
            optiontable = options.split('|||||')
            correct = optiontable[0]
            taskoptions = MultipleChoiceTask.objects.filter(task=task)
            newoptions = (len(optiontable)-1) - len(taskoptions)

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
                for option in optiontable[len(optiontable)-newoptions:]:
                    if int(correct) == x:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=True)
                    else:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=False)
                    multiplechoice.save()
                    x += 1
        return super(TaskUpdateView, self).form_valid(form)


class TestCreateView(generic.CreateView):
    template_name = 'maths/test_form.html'
    model = TestBase
    fields = ['test_name', 'tasks']
    success_url = reverse_lazy('maths:testList')

    def get_context_data(self, **kwargs):
        context = super(TestCreateView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        testBase = form.save(commit=False)
        testBase.author = self.request.user
        testBase.save()
        return super(TestCreateView, self).form_valid(form)


class TestListView(generic.ListView):
    template_name = 'maths/test_list.html'
    model = TestBase


class TestDetailView(generic.DetailView):
    template_name = 'maths/test_detail.html'
    model = TestBase
    pk_url_kwarg = 'test_pk'

    def get_context_data(self, **kwargs):
        context = super(TestDetailView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context




