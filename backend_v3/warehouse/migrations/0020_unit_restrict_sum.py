# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-04 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0019_auto_20180403_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='restrict_sum',
            field=models.BooleanField(default=False, verbose_name='Не суммировать'),
        ),
    ]