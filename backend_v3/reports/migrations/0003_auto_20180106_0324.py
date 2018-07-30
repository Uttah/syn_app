# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-06 00:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20171228_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'permissions': (('global_manage', 'Управление всеми отчетами'),), 'verbose_name': 'Отчет', 'verbose_name_plural': 'Отчеты'},
        ),
        migrations.AlterField(
            model_name='report',
            name='time_edited',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время изменения'),
        ),
    ]
