from django.views import generic
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from .models import Task
# Create your views here.


class IndexView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = 'maths/index.html'


class CreateTaskView(generic.CreateView):
    login_url = reverse_lazy('login')
    template_name = 'maths/task_form.html'
    model = Task
    fields = ['title', 'text', 'task_type']
    success_url = '/'

    def form_valid(self, form):
        task = form.save(commit=False)
        task.author = self.request.user
        task.save()
        return super(CreateTaskView, self).form_valid(form)
