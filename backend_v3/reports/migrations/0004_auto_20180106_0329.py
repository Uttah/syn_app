# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-06 00:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20180106_0324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='time_edited',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время изменения'),
        ),
    ]
