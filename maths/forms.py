from django import forms
from .models import Task, Category, MultipleChoiceTask, GeogebraTask


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
    preview = forms.CharField(max_length=500000)

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


class CreateTestForm(forms.Form):
    test_id = forms.IntegerField()
