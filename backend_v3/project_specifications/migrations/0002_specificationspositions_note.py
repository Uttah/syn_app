# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-20 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_specifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificationspositions',
            name='note',
            field=models.CharField(max_length=250, null=True, verbose_name='Комментарий'),
        ),
    ]
