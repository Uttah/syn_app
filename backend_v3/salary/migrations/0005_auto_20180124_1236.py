# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-24 09:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0004_gradecoefficient'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gradecoefficient',
            options={'verbose_name': 'Оценочный коэффициент', 'verbose_name_plural': 'Оценочные коэффициенты'},
        ),
        migrations.AlterField(
            model_name='gradecoefficient',
            name='time',
            field=models.IntegerField(verbose_name='Срок'),
        ),
    ]
