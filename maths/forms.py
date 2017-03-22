from django import forms
from .models import Task, Category, MultipleChoiceTask, GeogebraTask


class CreateTaskForm(forms.ModelForm):
    options = forms.CharField(max_length=10000, required=False)
    base64 = forms.CharField(max_length=32700, required=False)

    class Meta:
        model = Task
        fields = ['title', 'text', 'answertype', 'extra', 'reasoning', 'category']
