# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-18 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_auto_20180218_2219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='good',
            name='note',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Примечание'),
        ),
        migrations.AlterField(
            model_name='good',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Warehouse', verbose_name='Склад'),
        ),
    ]
