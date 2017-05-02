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


class Task(models.Model):
    """The base of a task

    :title: The title, max 100 letters
    :task_type: The task type, can be t.ex. functions or fractions
    :text: The text that describes what the task is, max 32700 letters
    :author: The person that made the task
    """
    title = models.CharField(max_length=100, default="")
    text = models.TextField(max_length=32700, blank=True)
    answertype = models.IntegerField()
    reasoning = models.BooleanField()
    extra = models.BooleanField()
    author = models.ForeignKey(Person)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return str(self.id) + " - " + self.title


class MultipleChoiceTask(models.Model):
    """
    Multiple choice options for a task

    :task: The task that the multiple choice options are for.
    :option: The multiple choice options
    :correct: The correct answer
    """
    task = models.ForeignKey(Task)
    option = models.CharField(max_length=500)
    correct = models.BooleanField()

    def __str__(self):
        return self.option


class GeogebraTask(models.Model):
    """
    Geogebra extension for a task

    :task: The task the geogebra extension belongs to.
    :base64: The geogebra string.
    """
    task = models.ForeignKey(Task)
    base64 = models.CharField(max_length=32700)
    preview = models.TextField(null=True)


class TaskCollection(models.Model):
    """
    A Collection of task, base of a test.

    :tasks: The tasks.
    :test_name: The name of the test.
    """
    tasks = models.ManyToManyField(Task, verbose_name='oppgaver')
    test_name = models.CharField(max_length=100, verbose_name='test navn')
    author = models.ForeignKey(Person)

    def __str__(self):
        return self.test_name + " - " + self.author.get_full_name()

    def get_absolute_url(self):
        """
            Function that sets the absolute_url.
        """
        return reverse('maths:taskCollectionDetail', kwargs={'taskCollection_pk': self.id})


class Test(models.Model):
    """
    A test.
    
    :taskCollection: The collection of tasks, base of the test.
    :published: Date the test was published.
    :dueDate: Due date for the test
    :randomOrder: Says if the order of the tasks should be in a random order or not.
   
    """
    task_collection = models.ForeignKey(TaskCollection)
    published = models.DateTimeField(verbose_name='Publisert')
    dueDate = models.DateTimeField(verbose_name='Siste frist for besvarelse', null=True, blank=True)
    randomOrder = models.BooleanField(default=False, verbose_name='Tilfeldig rekkefølge',
                                      help_text='Dersom avkrysset vil testen bli gitt i tilfeldig rekkefølge.')
    strictOrder = models.BooleanField(default=False, verbose_name='Lås rekkefølge')

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.task_collection.test_name


class TaskOrder(models.Model):
    """
    Order of the tasks in a test. Uses the order in the database.

    :test: The test the task is in.
    :task: The task
    """
    test = models.ForeignKey(Test)
    task = models.ForeignKey(Task)
    order = models.IntegerField()


class Answer(models.Model):
    """
    The answer of a task in a test.

    :task: The task.
    :test: The test the task is in.
    :user: The user that answered.
    :reasoning: Users reasoning behind the answer.
    :text: The answer.
    """
    task = models.ForeignKey(Task)
    test = models.ForeignKey(Test)
    user = models.ForeignKey(Person)
    reasoning = models.CharField(max_length=32700, null=True)
    text = models.CharField(max_length=32700, null=True)


class GeogebraAnswer(models.Model):
    """
    Geogebra extention for an answer.

    :answer: The answer.
    :base64: The base64 string.
    """
    answer = models.ForeignKey(Answer)
    base64 = models.CharField(max_length=32700)
