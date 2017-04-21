from django import forms
from .models import Task, Category, MultipleChoiceTask, GeogebraTask, Test, Answer
from administration.models import Person, Grade, School, Gruppe
from django.forms import inlineformset_factory


class CreateTaskForm(forms.ModelForm):
    """
    Form used to create a new task.

    :title: Title of the task.
    :text: Description of the task.
    :answertype: Answer details for the answer.
    :extra: Show extra extensions (geogebra).
    :reasoning: Show a field for an explanation of the answer.
    :category: Which categories the task fall under.
    :options: Multiple choice options for the task.
    :base64: Geogebra string.

    """
    options = forms.CharField(max_length=10000, required=False)
    base64 = forms.CharField(max_length=32700, required=False)
    preview = forms.CharField(max_length=500000, required=False)

    class Meta:
        """
            Bases the form on the Task model
        """
        model = Task
        fields = ['title', 'text', 'answertype', 'extra', 'reasoning', 'category']


class CreateCategoryForm(forms.ModelForm):
    """
    Form used to create a new category.

    :category_title: Title of the category.
    """

    class Meta:
        """
           Bases the form on the Category model
        """
        model = Category
        fields = ['category_title']


class CreateTestForm(forms.ModelForm):
    persons = forms.ModelMultipleChoiceField(queryset=Person.objects.filter(role__in=[1, 2]), required=False)
    grades = forms.ModelMultipleChoiceField(queryset=Grade.objects.all(), required=False)
    schools = forms.ModelMultipleChoiceField(queryset=School.objects.all(), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Gruppe.objects.all(), required=False)
    order = forms.CharField(max_length=100)

    class Meta:
        model = Test
        fields = ['task_collection', 'randomOrder', 'published', 'dueDate']


class CreateAnswerForm(forms.ModelForm):
    base64answer = forms.CharField(max_length=500000, required=False)
    reasoning = forms.CharField(max_length=32700, required=False)
    text = forms.CharField(max_length=32700, required=False)

    class Meta:
        model = Answer
        fields = ['task', 'reasoning', 'text']
