# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-15 08:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0010_auto_20170612_1717'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskcollection',
            name='tasks',
        ),
    ]