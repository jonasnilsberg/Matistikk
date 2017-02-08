from django.views import generic

from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.core.urlresolvers import reverse_lazy


class LoginView(generic.FormView):
    template_name = 'administration/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

