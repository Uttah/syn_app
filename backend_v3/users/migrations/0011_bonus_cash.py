# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-16 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20180313_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonus',
            name='cash',
            field=models.BooleanField(default=False, verbose_name='Наличными'),
        ),
    ]
