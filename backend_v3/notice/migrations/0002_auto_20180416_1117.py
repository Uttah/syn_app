# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-16 08:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='confirmed',
            field=models.BooleanField(default=False, verbose_name='Подтверждено'),
        ),
    ]
