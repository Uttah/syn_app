# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-15 06:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0016_auto_20180510_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferposition',
            name='count',
            field=models.FloatField(verbose_name='Количество'),
        ),
    ]
