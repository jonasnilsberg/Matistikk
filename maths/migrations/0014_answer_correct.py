# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-20 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0013_auto_20170616_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='correct',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
