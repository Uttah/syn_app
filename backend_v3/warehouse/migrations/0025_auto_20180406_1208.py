# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-06 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0024_auto_20180406_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodposition',
            name='good_kind',
        ),
        migrations.RemoveField(
            model_name='specificationspositions',
            name='good_position',
        ),
        migrations.AddField(
            model_name='specificationspositions',
            name='description_info',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Тип, марка, обозначение документа, опросного листа'),
        ),
        migrations.DeleteModel(
            name='GoodPosition',
        ),
    ]
