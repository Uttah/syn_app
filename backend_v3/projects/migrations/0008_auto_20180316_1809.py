# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-16 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20180315_1403'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['number'], 'permissions': (('global_analysis', 'Анализ всех проектов'), ('change_project_state_batch', 'Изменять этап проекта в записях табеля'), ('change_project_state', 'Может изменять этапы проекта в списке проектов')), 'verbose_name': 'Проект', 'verbose_name_plural': 'Проекты'},
        ),
    ]
