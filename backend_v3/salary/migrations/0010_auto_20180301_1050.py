# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-01 07:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0009_auto_20180212_1538'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salaryarchive',
            options={'permissions': (('generate_b7_export', 'Может экспортировать в Б7'),)},
        ),
    ]
