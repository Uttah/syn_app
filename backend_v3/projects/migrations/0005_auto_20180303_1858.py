# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-03 15:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20180115_1545'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['number'], 'permissions': (('global_analysis', 'Анализ всех проектов'),), 'verbose_name': 'Проект', 'verbose_name_plural': 'Проекты'},
        ),
    ]
