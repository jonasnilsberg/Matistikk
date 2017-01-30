from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Create your models here.


class AssignmentBase(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)

    def __str__(self):
        return self.title


class GeogebraAssignment(models.Model):
    assignmentBase = models.ForeignKey(AssignmentBase)
    solution = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.assignmentBase.title


class Test(models.Model):
    title = models.CharField(max_length=100)
    assignments = models.ManyToManyField(AssignmentBase)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('calculations:detail', kwargs={'pk': self.pk})


class TestView(models.Model):
    test = models.ForeignKey(Test)
    assignmentOrder = models.CharField(max_length=100)


# Answers ------------------------------------------------------------------------------------------------------------

class AnswerBase(models.Model):
    user = models.ForeignKey(User)
    assignment = models.ForeignKey(AssignmentBase)
    testView = models.ForeignKey(TestView)

    def __str__(self):
        return "Answer - " + self.assignment.title


class GeogebraAnswer(models.Model):
    answer_base = models.ForeignKey(AnswerBase)
    answer = models.CharField(max_length=100)

    def __str__(self):
        return "Answer - " + self.answer_base.assignment.title

# ------------------------------------------------------------------------------------------------------------------------------------


class School(models.Model):
    school_name = models.CharField(max_length=100)
    school_address = models.CharField(max_length=100)

    def __str__(self):
        return self.school_name


class Grade(models.Model):
    school = models.ForeignKey(School)
    grade_name = models.CharField(max_length=100)
    tests = models.ManyToManyField(Test)

    def __str__(self):
        return self.school.school_name + " - " + self.grade_name


class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, default="", blank=True, null=True)
    SEX = [
        ("M", "Gutt"),
        ("F", "Jente")
    ]
    sex = models.CharField(max_length=1, choices=SEX)

    def __str__(self):
        return self.user.username


