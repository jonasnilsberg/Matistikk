# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-26 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0031_auto_20170726_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputfield',
            name='correct',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
