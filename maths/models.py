from administration.models import Person
from django.db import models


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


class Test(models.Model):
    """
    A test is a collection of tasks.

    :tasks: The tasks.
    :test_name: The name of the test.
    """
    tasks = models.ManyToManyField(Task, verbose_name='oppgaver')
    test_name = models.CharField(max_length=100, verbose_name='test navn')
    author = models.ForeignKey(Person)

    def __str__(self):
        return self.test_name + " - " + self.author.get_full_name()


class TestDisplay(models.Model):
    test = models.ForeignKey(Test)
    published = models.DateField(verbose_name='Publisert')


class TaskOrder(models.Model):
    test_display = models.ForeignKey(TestDisplay)
    task = models.ForeignKey(Task)
    order = models.IntegerField()

