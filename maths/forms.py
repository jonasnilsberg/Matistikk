from django import forms
from .models import Task, Category, MultipleChoiceTask, GeogebraTask, Test, Answer, TaskLog
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
    :variableDescription: Description of the variables for GeoGebra.
    :reasoningText: Title for the reasoning answer-field.
    :options: Multiple choice options for the task.
    :base64: Geogebra string.
    :preview: PNG base64 string for GeoGebra.
    :create_new: Create new task or update the existing one.
    :questions: Questions for multiple-choice.
    :correct: Says which options are correct.
    :variables: Variables for Geogebra.
    :height: Dimension of the GeoGebra applet.
    :width: Dimension of the GeoGebra applet.
    :showMenuBar: Settings for GeoGebra - showMenuBar.
    :enableLabelDrags: Settings for GeoGebra - enableLabelDrags.
    :enableShiftDragZoom: Settings for GeoGebra - enableShiftDragZoom.
    :enableRightClick: Settings for GeoGebra - enableRightClick.
    """
    options = forms.CharField(max_length=100000, required=False)
    base64 = forms.CharField(max_length=200000, required=False)
    preview = forms.CharField(max_length=500000, required=False)
    create_new = forms.BooleanField(required=False)
    questions = forms.CharField(max_length=100000, required=False)
    correct = forms.CharField(max_length=100000, required=False)
    variables = forms.CharField(max_length=500, required=False)
    inputQuestion = forms.CharField(max_length=500, required=False)
    inputField = forms.CharField(max_length=500, required=False)
    inputLength = forms.CharField(max_length=500, required=False)
    inputCorrect = forms.CharField(max_length=500, required=False)
    inputFraction = forms.CharField(max_length=500, required=False)
    inputScore = forms.CharField(max_length=500, required=False)
    height = forms.CharField(max_length=100, required=False)
    width = forms.CharField(max_length=100, required=False)
    imageFile = forms.FileField(required=False)
    jsFile = forms.FileField(required=False)
    xmin = forms.FloatField(required=False)
    xmax = forms.FloatField(required=False)
    ymin = forms.FloatField(required=False)
    ymax = forms.FloatField(required=False)
    yratio = forms.FloatField(required=False)
    xstep = forms.FloatField(required=False)
    ystep = forms.FloatField(required=False)
    showMenuBar = forms.BooleanField(initial=False, required=False)
    enableLabelDrags = forms.BooleanField(initial=True, required=False)
    enableShiftDragZoom = forms.BooleanField(initial=True, required=False)
    enableRightClick = forms.BooleanField(initial=True, required=False)
    algebraInputField = forms.BooleanField(initial=False, required=False)
    radioOrCheck = forms.CharField(max_length=500, required=False)

    class Meta:
        """
            Bases the form on the Task model
        """
        model = Task
        fields = ['title', 'text', 'answertype', 'extra', 'reasoning', 'category', 'variableDescription',
                  'reasoningText', 'directory', 'answerText']


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


class CreateTaskLog(forms.ModelForm):
    class Meta:
        model = TaskLog
        fields = ['text']


class CreateTestForm(forms.ModelForm):
    """
    Form used to create a new test.

    :persons: All the persons the test can be published to.
    :grades: All the grades the test can be published to.
    :schools: All the schools the test can be published to.
    :groups: All the groups the test can be published to.
    :order: The order of the tasks in test, if randomOrder is not True.
    :task_collection: The collection of the tasks (Base of the test).
    :randomOrder: Says if the order of the tasks should be random or in a given order.
    :published: Date the test is published.
    :dueDate: Due date for the test.
    """
    persons = forms.ModelMultipleChoiceField(queryset=Person.objects.filter(role__in=[1, 2]), required=False)
    grades = forms.ModelMultipleChoiceField(queryset=Grade.objects.all(), required=False)
    schools = forms.ModelMultipleChoiceField(queryset=School.objects.all(), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Gruppe.objects.all(), required=False)
    order = forms.CharField(max_length=10000)

    class Meta:
        model = Test
        fields = ['task_collection', 'randomOrder', 'published', 'dueDate', 'strictOrder']


class CreateAnswerForm(forms.ModelForm):
    """
    Form used to create a new answer.

    :base64answer: The base64 string from geogebra.
    :reasoning: The reasoning behind the answer.
    :text: The answer.
    :task: The task the answer matches to.
    """
    testanswer = forms.CharField()
    base64answer = forms.CharField(max_length=500000, required=False)
    reasoning = forms.CharField(max_length=32700, required=False)
    text = forms.CharField(max_length=32700, required=False)
    timespent = forms.FloatField(required=False)
    geogebradata = forms.CharField(max_length=500000, required=False)
    correct = forms.CharField(max_length=100, required=False)
    variables = forms.CharField(max_length=1000, required=False)
    matistikkanswer = forms.CharField(max_length=500, required=False)
    xmin = forms.FloatField(required=False)
    xmax = forms.FloatField(required=False)
    ymin = forms.FloatField(required=False)
    ymax = forms.FloatField(required=False)
    yratio = forms.FloatField(required=False)

    class Meta:
        model = Answer
        fields = ['reasoning', 'text', 'timespent', 'item']


class CreateTestAnswerForm(forms.Form):
    testAnswer_id = forms.CharField()

