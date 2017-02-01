"""Views that handel administration """

# Core Django imports
from django.views.generic import CreateView

#Third-party app imports
from braces.views import StaffuserRequiredMixin

#Imports from the projects own apps
from .models import Person


class PersonCreateView(StaffuserRequiredMixin, CreateView):
    """Handles the creation of a new person to the database, uses the braces mixin StaffuserRequiredMixin to check if the
    user that sent the request has permissions to do so
    :login_url:
    :template_name: points to the html file you want to be rendered
    :model: what model does the form is based on
    :fields: what fields the user is asked to fill in
    :success_url: Where the user is sent upon successfully creating a new user"""

    login_url = '/'
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'grade']
    success_url = '/maths'

    def form_valid(self, form):
        return super(PersonCreateView, self).form_valid(form)





