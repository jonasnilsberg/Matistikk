from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login


class LoginView(FormView):
    template_name = 'administration/login.html'
    form_class = AuthenticationForm
    success_url = 'maths'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())