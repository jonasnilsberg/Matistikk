from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Create your models here.


class AssignmentBase(models.Model):
    title = models.CharField(max_length=100, default="")
    description = models.TextField(max_length=1000, null=True)

    class Meta:
        abstract = True


class GeogebraAssignment(AssignmentBase):
    solution = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.assignmentBase.title


class Test(models.Model):
    title = models.CharField(max_length=100)
    geogebraAssignments = models.ManyToManyField(GeogebraAssignment)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('calculations:detail', kwargs={'pk': self.pk})


class TestView(models.Model):
    test = models.ForeignKey(Test)
    assignmentOrder = models.CharField(max_length=100)


# Answers ------------------------------------------------------------------------------------------------------------

class AnswerBase(models.Model):
    user = models.ForeignKey(User, default="")
    testView = models.ForeignKey(TestView, default="")

    class Meta:
        abstract = True


class GeogebraAnswer(AnswerBase):
    assignment = models.ForeignKey(GeogebraAssignment, default="", on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)

    def __str__(self):
        return "Answer - " + self.answer_base.assignment.title

# ------------------------------------------------------------------------------------------------------------------------------------

