from django.views import generic
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from .forms import CreateTaskForm
from .models import Task, MultipleChoiceTask, Category, GeogebraTask
# Create your views here.


class IndexView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = 'maths/index.html'


class CreateTaskView(generic.CreateView):
    login_url = reverse_lazy('login')
    template_name = 'maths/task_form.html'
    form_class = CreateTaskForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CreateTaskView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
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


class TaskListView(generic.ListView):
    login_url = reverse_lazy('login')
    template_name = 'maths/task_list.html'
    model = Task
