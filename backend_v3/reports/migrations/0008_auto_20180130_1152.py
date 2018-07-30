# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-30 08:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_auto_20180124_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subprocess',
            name='kind',
            field=models.CharField(blank=True, choices=[('D', 'Вождение'), ('A', 'Сборка'), ('P', 'Проектирование'), ('W', 'Работа на объекте')], max_length=1, null=True, verbose_name='Тип'),
        ),
    ]