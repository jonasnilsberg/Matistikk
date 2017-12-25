from administration.models import Person
from django.db import models
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta, timezone


# Create your models here.


class Category(models.Model):
    """
    A category

    :category: The name of the category
    """
    category_title = models.CharField(max_length=50, verbose_name="kategori")

    class Meta:
        ordering = ['category_title']

    def __str__(self):
        return self.category_title


class Directory(models.Model):
    name = models.CharField(max_length=500)
    parent_directory = models.ForeignKey('self', blank=True, null=True)
    date_created = models.DateTimeField()
    author = models.ForeignKey(Person, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        path_tab = self.path()
        path = ""
        for name in path_tab:
            path += name + " / "
        return path + self.name

    def path(self):
        path = []
        parent = True
        if self.parent_directory:
            parent_directory = self.parent_directory
            while parent:
                if parent_directory:
                    path.insert(0, parent_directory.name)
                    parent_directory = parent_directory.parent_directory
                else:
                    parent = False
        return path


class Task(models.Model):
    """The base of a task

    :title: The title, max 100 letters
    :text: The text that describes what the task is, max 20 000 letters
    :answertype: What kind of answer should the user give. (text, multiple choice etc.)
    :reasoning: Reason behind the users answer.
    :extra: Says if the tasks contains any extra information (geogebra etc.)
    :author: The person that made the task
    :category: Which categories fits the task. 
    """
    title = models.CharField(max_length=100, default="")
    text = models.TextField(max_length=15000, blank=True)
    answerText = models.CharField(max_length=200, null=True, blank=True)
    answertype = models.IntegerField()
    reasoning = models.BooleanField()
    reasoningText = models.CharField(max_length=1000, blank=True)
    EXTRA = [
        (1, "GeoGebra"),
        (2, 'Bildeopplastning'),
        (3, 'Filopplastning'),
        (4, 'Ingen tillegg'),
    ]
    extra = models.BooleanField()
    extraNew = models.IntegerField(choices=EXTRA, default=1)
    variableTask = models.BooleanField(default=False)
    variableDescription = models.CharField(max_length=10000, null=True, blank=True)
    author = models.ForeignKey(Person)
    category = models.ManyToManyField(Category)
    directory = models.ForeignKey(Directory)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.id) + " - " + self.title


class TaskLog(models.Model):
    text = models.TextField(max_length=1000, verbose_name='Kommentar...')
    task = models.ForeignKey(Task)
    author = models.ForeignKey(Person)
    date = models.DateTimeField()


class Item(models.Model):
    task = models.ForeignKey(Task)
    random_variables = models.BooleanField(default=False)
    variables = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        if self.variables:
            return str(self.id) + " - " + self.task.title + " - (" + self.variables + ')'
        else:
            return str(self.id) + " - " + self.task.title


class InputFieldTask(models.Model):
    task = models.ForeignKey(Task)
    question = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return self.task.__str__() + ": " + self.question


class InputField(models.Model):
    """
    Input field for a task

    :inputFieldTask: The inputfieldtask that the inputfield is for.
    :title: The title for the inputfield.
    """
    inputFieldTask = models.ForeignKey(InputFieldTask)
    title = models.CharField(max_length=200, blank=True)
    inputnr = models.IntegerField(null=True)
    inputlength = models.IntegerField(default=10)
    correct = models.CharField(max_length=100, null=True, blank=True)
    score = models.IntegerField(default=1)
    fraction = models.BooleanField(default=False)

    def __str__(self):
        return self.inputFieldTask.__str__() + " - " + self.title


class MultipleChoiceTask(models.Model):
    """Multiple choice options for a task

    :task: The task that the multiple choice options are for.
    :option: The multiple choice options
    :correct: The correct answer
    """
    task = models.ForeignKey(Task)
    question = models.CharField(max_length=500, blank=True)
    checkbox = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' - Svaralternativer: ' + str(self.task)


class MultipleChoiceOption(models.Model):
    MutipleChoiceTask = models.ForeignKey(MultipleChoiceTask)
    option = models.CharField(max_length=500)
    correct = models.BooleanField()

    def __str__(self):
        return 'Svaralternativ ' + self.option + ' for oppgave: ' + str(self.MutipleChoiceTask.task)


class GeogebraTask(models.Model):
    """
    Geogebra extension for a task

    :task: The task the geogebra extension belongs to.
    :base64: The geogebra string.
    :preview: Preview of the geogebra, in form of an image. 
    """
    task = models.ForeignKey(Task)
    height = models.CharField(max_length=100, null=True)
    width = models.CharField(max_length=100, null=True)
    xmin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    yratio = models.FloatField(default=1)
    xstep = models.FloatField(default=1)
    ystep = models.FloatField(default=1)
    showMenuBar = models.BooleanField(default=False)
    enableLabelDrags = models.BooleanField(default=True)
    enableShiftDragZoom = models.BooleanField(default=True)
    enableRightClick = models.BooleanField(default=True)
    base64 = models.TextField(null=True)
    preview = models.TextField(null=True)

    def __str__(self):
        return "Geogebra: " + self.task.title


class TaskCollection(models.Model):
    """
    A Collection of task, base of a test.

    :tasks: The tasks.
    :test_name: The name of the test.
    :author: The person that created the Task Collection.
    """
    items = models.ManyToManyField(Item)
    test_name = models.CharField(max_length=100, verbose_name='test navn')
    author = models.ForeignKey(Person)

    def __str__(self):
        return self.test_name + " - " + self.author.get_full_name()

    def get_absolute_url(self):
        """
            Function that sets the absolute_url.
        """
        return reverse('maths:taskCollectionDetail', kwargs={'taskCollection_pk': self.id})

    class Meta:
        ordering = ["-id"]


class Test(models.Model):
    """
    A test.
    
    :taskCollection: The collection of tasks, base of the test.
    :published: Date the test was published.
    :dueDate: Due date for the test
    :randomOrder: Says if the order of the tasks should be in a random order or not.
    :strictOrder: Says if the order of the tasks should be locked in a chronological order. 
    """

    task_collection = models.ForeignKey(TaskCollection)
    published = models.DateTimeField(verbose_name='Publisert')
    dueDate = models.DateTimeField(verbose_name='Siste frist for besvarelse', null=True, blank=True)
    randomOrder = models.BooleanField(default=False, verbose_name='Tilfeldig rekkefølge',
                                      help_text='Dersom avkrysset vil testen bli gitt i tilfeldig rekkefølge.')
    strictOrder = models.BooleanField(default=False, verbose_name='Lås rekkefølge')
    public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.task_collection.test_name

    def get_absolute_url(self):
        return reverse('maths:testDetail', kwargs={'test_pk': self.id})


class TaskOrder(models.Model):
    """
    Order of the tasks in a test. Uses the order in the database.

    :test: The test the task is in.
    :task: The task
    """
    test = models.ForeignKey(Test)
    item = models.ForeignKey(Item, null=True)

    def __str__(self):
        return str(self.test.id) + " - " + self.test.task_collection.test_name + " - " + self.item.task.title + str(
            self.id)


class Answer(models.Model):
    """
    The answer of a task in a test.

    :task: The task.
    :test: The test the task is in.
    :user: The user that answered.
    :reasoning: Users reasoning behind the answer.
    :text: The answer.
    """
    item = models.ForeignKey(Item)
    test = models.ForeignKey(Test)
    user = models.ForeignKey(Person, null=True)
    anonymous_user = models.IntegerField(null=True)
    reasoning = models.CharField(max_length=6000, null=True)
    text = models.CharField(max_length=6000, null=True)
    date_answered = models.DateTimeField(null=True)
    timespent = models.FloatField(null=True)
    correct = models.CharField(max_length=100, null=True, default=None)

    def __str__(self):
        if self.user:
            return "Svar: " + self.test.task_collection.test_name + " - " + self.item.task.title + " - " + self.user.get_full_name()
        else:
            return "Svar: " + self.test.task_collection.test_name + " - " + self.item.task.title + " - Anonym bruker: " + str(
                self.anonymous_user)


class GeogebraAnswer(models.Model):
    """
    Geogebra extention for an answer.

    :answer: The answer.
    :base64: The base64 string.
    :data: How the user used geogebra to solve the task. (Data from listeners)
    """
    answer = models.ForeignKey(Answer)
    matistikkAnswer = models.CharField(max_length=500, null=True)
    base64 = models.TextField()
    data = models.TextField(null=True)

    def __str__(self):
        if self.answer.user:
            return "Geogebra: " + self.answer.test.task_collection.test_name + " - " + self.answer.item.task.title + " - " + self.answer.user.get_full_name()
        else:
            return "Geogebra: " + self.answer.test.task_collection.test_name + " - " + self.answer.item.task.title + " - Anonym bruker: " + str(
                self.answer.anonymous_user)


class LogitTestItem(models.Model):
    """
    Logit for an item in a test.

    :test: The test.
    :item: The item.
    :logit: logit score.
    """
    test = models.ForeignKey(Test)
    item = models.ForeignKey(Item)
    logit = models.FloatField()


class LogitTestPerson(models.Model):
    """
    Logit for a person on a test.

    :test: The test.
    :item: The person.
    :logit: logit score.
    """
    test = models.ForeignKey(Test)
    person = models.ForeignKey('administration.Person')
    logit = models.FloatField()
