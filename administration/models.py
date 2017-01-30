from django.db import models
from django.contrib.auth.models import User
from maths.models import Test
# Create your models here.


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

