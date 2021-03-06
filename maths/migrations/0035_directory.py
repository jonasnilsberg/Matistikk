# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-08 07:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0034_auto_20170727_1002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('date_created', models.DateTimeField()),
                ('parent_directory', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='maths.Directory')),
                ('tasks', models.ManyToManyField(to='maths.Task')),
            ],
        ),
    ]
