# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-21 11:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0012_auto_20180321_1421'),
    ]

    operations = [
        migrations.RenameField(
            model_name='good',
            old_name='warehouse',
            new_name='location',
        ),
        migrations.AddField(
          model_name='goodkind',
          name='new',
          field=models.BooleanField(default=True, verbose_name='Новый'),
        ),
    ]
