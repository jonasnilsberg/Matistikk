# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-27 08:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0033_inputfield_fraction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputfield',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
