from administration.models import Person
from django.db import models


# Create your models here.


class Task(models.Model):
    """The base of a task

    :title: The title, max 100 letters
    :task_type: The task type, can be t.ex. functions or fractions
    :text: The text that describes what the task is, max 32700 letters
    :author: The person that made the task
    """
    title = models.CharField(max_length=100, default="")
    task_type = models.IntegerField()
    text = models.TextField(max_length=32700, blank=True)
    author = models.ForeignKey(Person)
