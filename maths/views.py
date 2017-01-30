from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def IndexView(request):

    template_name = 'maths/base.html'
    return render(request, template_name)