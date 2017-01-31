from django.db import models
from django.contrib.auth.models import User
from maths.models import Test
from django.utils.translation import ugettext_lazy as _

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


class Student(User):
    grade = models.ForeignKey(Grade, default="", blank=True, null=True, verbose_name="klasse")
    SEX = [
        ("M", "Gutt"),
        ("F", "Jente")
    ]
    sex = models.CharField(max_length=1, choices=SEX, )

    def __str__(self):
        return self.username

Student._meta.get_field('username').verbose_name = 'brukernavn'
Student._meta.get_field('first_name').verbose_name = 'fornavn'
Student._meta.get_field('last_name').verbose_name = 'etternavn'
Student._meta.get_field('is_staff').verbose_name = 'lærer'