from administration.models import Person
from django.db import models


# Create your models here.


class Category(models.Model):
    """
    :category: The name of the category
    """
    category = models.CharField(max_length=50, verbose_name="kategori")

    class Meta:
        ordering = ['category']

    def __str__(self):
        return self.category


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
    task = models.ForeignKey(Task)
    option = models.CharField(max_length=500)
    correct = models.BooleanField()

    def __str__(self):
        return self.option
