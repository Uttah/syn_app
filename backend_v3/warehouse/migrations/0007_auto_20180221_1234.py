# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-21 09:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0006_auto_20180219_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='good',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Warehouse', verbose_name='Склад'),
        ),
        migrations.AlterField(
            model_name='goodkind',
            name='code',
            field=models.CharField(max_length=100, null=True, unique=True, verbose_name='Артикул'),
        ),
    ]
