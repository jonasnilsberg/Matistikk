# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-08 08:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0035_directory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='parent_directory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maths.Directory'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='tasks',
            field=models.ManyToManyField(blank=True, to='maths.Task'),
        ),
    ]
