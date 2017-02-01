"""The models that are mainly used in the administration app"""

# Core Django imports
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class School(models.Model):
    """A school
    :school_name: The name of the school
    :school_address: The address of the school"""

    school_name = models.CharField(max_length=100)
    school_address = models.CharField(max_length=100)

    def __str__(self):
        return self.school_name


class Grade(models.Model):
    """ A grade is a group of students
    :school: the school object the grade relates to
    :grade_name the name identifies the grade within the school
    :tests = which tests this class has been given access to. """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    grade_name = models.CharField(max_length=100)
    tests = models.ManyToManyField('maths.TestView')

    def __str__(self):
        return self.school.school_name + " - " + self.grade_name


class Person(AbstractUser):
    """A person is a customUser modal, it contains information about the user that does not relate to user-management.
    :grade: The grade this person is registered to
    :SEX: The sex of the person."""

    grade = models.ForeignKey(Grade, default="", blank=True, null=True, verbose_name="klasse")
    SEX = [
        ("M", "Gutt"),
        ("F", "Jente")
    ]
    sex = models.CharField(max_length=1, choices=SEX, verbose_name="kjonn", null=True)

    def __str__(self):
        return self.username

#This is in order to have different names shown by the django-forms than variable-names
Person._meta.get_field('username').verbose_name = 'brukernavn'
Person._meta.get_field('first_name').verbose_name = 'fornavn'
Person._meta.get_field('last_name').verbose_name = 'etternavn'
Person._meta.get_field('is_staff').verbose_name = 'laerer'
Person._meta.get_field('email').verbose_name = 'Epost'