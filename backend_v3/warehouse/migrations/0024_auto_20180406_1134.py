# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-06 08:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0023_auto_20180405_1219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodposition',
            name='unit',
        ),
        migrations.AddField(
            model_name='specificationspositions',
            name='good_kind',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.GoodKind', verbose_name='Вид товара'),
        ),
        migrations.AddField(
            model_name='specificationspositions',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='warehouse.Unit', verbose_name='Единица измерения'),
        ),
    ]
