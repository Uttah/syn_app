# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-09 12:20
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0027_auto_20180409_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specification',
            name='dates',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None),
        ),
    ]
