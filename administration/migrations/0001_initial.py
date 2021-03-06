# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-08 07:53
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('sex', models.CharField(choices=[('M', 'Gutt'), ('F', 'Jente')], max_length=1, null=True, verbose_name='kjønn')),
                ('date_of_birth', models.DateField(max_length=8, null=True, verbose_name='Fødselsdato')),
                ('role', models.IntegerField(choices=[(1, 'Elev'), (2, 'Lærer'), (3, 'Skoleadministrator'), (4, 'Administrator')], default=1, verbose_name='brukertype')),
            ],
            options={
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_name', models.CharField(max_length=100, verbose_name='klassenavn')),
                ('is_active', models.BooleanField(default=True, help_text='Angir at denne klassen er aktiv. Avmerk denne i stedet for å slette klassen.', verbose_name='aktiv')),
            ],
            options={
                'ordering': ['school_id', 'grade_name'],
            },
        ),
        migrations.CreateModel(
            name='Gruppe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=100, verbose_name='Gruppenavn')),
                ('is_active', models.BooleanField(default=True, help_text='Angir at denne gruppen er aktiv. Avmerk denne i stedet for å slette gruppen.', verbose_name='aktiv')),
                ('visible', models.BooleanField(default=False, help_text='Angir om gruppen skal være synlig for sine medlemmer.', verbose_name='synlig')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Ansvarlig')),
                ('grade', models.ForeignKey(blank=True, help_text='Ikke påkrevd.', null=True, on_delete=django.db.models.deletion.CASCADE, to='administration.Grade', verbose_name='klasse')),
                ('persons', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Medlemmer')),
            ],
            options={
                'ordering': ['group_name'],
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(max_length=100, verbose_name='Navn')),
                ('school_address', models.CharField(max_length=100, verbose_name='Adresse')),
                ('is_active', models.BooleanField(default=True, help_text='Angir at denne skolen er aktiv. Avmerk denne i stedet for å slette skolen.', verbose_name='aktiv')),
                ('school_administrator', models.ForeignKey(blank=True, help_text='Ikke påkrevd. Opprett en ny skoleadministrator ved å trykke på plusstegnet til høyre.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Skoleadministrator')),
            ],
            options={
                'ordering': ['school_name'],
            },
        ),
        migrations.AddField(
            model_name='grade',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.School'),
        ),
        migrations.AddField(
            model_name='person',
            name='grades',
            field=models.ManyToManyField(blank=True, default='', to='administration.Grade', verbose_name='klasse'),
        ),
        migrations.AddField(
            model_name='person',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='person',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
