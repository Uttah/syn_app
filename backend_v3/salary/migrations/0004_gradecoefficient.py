# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-24 07:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0003_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeCoefficient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality', models.IntegerField(verbose_name='Качество')),
                ('time', models.IntegerField(verbose_name='Время')),
                ('coefficient', models.FloatField(verbose_name='Коэффициент')),
            ],
        ),
    ]
