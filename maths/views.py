from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
# Create your views here.


class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'maths/index.html'



