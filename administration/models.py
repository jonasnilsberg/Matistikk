"""The models that are mainly used in the administration app"""

# Core Django imports
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.urlresolvers import reverse
import datetime
from matistikk import settings


class School(models.Model):
    """A school

    :school_name: The name of the school
    :school_address: The address of the school
    """
    school_administrator = models.ForeignKey('Person', null=True, blank=True, verbose_name='Skoleadministrator', help_text='Ikke påkrevd.')
    school_name = models.CharField(max_length=100, verbose_name='Navn')
    school_address = models.CharField(max_length=100, verbose_name='Adresse')
    is_active = models.BooleanField(default=True, verbose_name='aktiv', help_text='Angir at denne skolen er aktiv. Avmerk denne i stedet for å slette kontoen.')

    class Meta:
        ordering = ['school_name']

    def __str__(self):
        return self.school_name

    def get_absolute_url(self):
        return reverse('administration:schoolDetail', kwargs={'school_pk': self.id})


class Grade(models.Model):
    """ A grade is a group of students

    :school: The school object the grade relates to

    :grade_name: The name name of the grade

    :tests: Which tests this class has been given access to. """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    grade_name = models.CharField(max_length=100, verbose_name='klassenavn')
    tests = models.ManyToManyField('maths.TestView', blank=True, verbose_name='tester')
    is_active = models.BooleanField(default=True, verbose_name='aktiv', help_text='Angir at denne skolen er aktiv. Avmerk denne i stedet for å slette kontoen.')

    class Meta:
        ordering = ['school_id', 'grade_name']

    def __str__(self):
        return self.school.school_name + " - " + self.grade_name


class Person(AbstractUser):
    """A person is a customUser model, it contains information about the user that does not relate to user-management.

    :grade: The grade this person is registered to
    :Sex: The sex of the person.
    """

    grades = models.ManyToManyField(Grade, default="", blank=True, verbose_name="klasse")
    SEX = [
        ("M", "Gutt"),
        ("F", "Jente")
    ]
    ROLE = [
        (1, "Elev"),
        (2, 'Lærer'),
        (3, 'Skoleadministrator'),
        (4, 'Administrator')
    ]
    sex = models.CharField(max_length=1, choices=SEX, verbose_name="kjønn", null=True)
    date_of_birth = models.DateField(max_length=8, verbose_name='Fødselsdato', null=True)
    role = models.IntegerField(choices=ROLE, default=1, verbose_name='brukertype')

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.first_name + " " + self.last_name + " - " + self.username

    def get_absolute_url(self):
        return reverse('administration:personDetail', kwargs={'slug': self.username})

    def createusername(self):
        first_name_form = self.first_name
        last_name_form = self.last_name
        first_name = first_name_form.replace(" ", "")
        first_name_lower = first_name.lower()
        last_name_lower = last_name_form.lower()
        last_name_tab = str.split(last_name_lower)
        username = first_name_lower
        for letter in last_name_tab:
            username += letter[0]
        last_name_list = list(last_name_tab[-1])
        for letter in last_name_list[1:]:
            if Person.objects.filter(username__exact=username):
                username += letter
            else:
                self.username = username
                break
        counter = 1
        username_correct = username
        while Person.objects.filter(username__exact=username_correct):
            username_correct = username + str(counter)
            counter += 1
        return username_correct



#This is in order to have different names shown by the django-forms than variable-names
Person._meta.get_field('username').verbose_name = 'brukernavn'
Person._meta.get_field('first_name').verbose_name = 'fornavn'
Person._meta.get_field('last_name').verbose_name = 'etternavn'
Person._meta.get_field('is_staff').verbose_name = 'lærer'
Person._meta.get_field('email').verbose_name = 'Epost'

