# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-25 11:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0036_location_responsible'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goodgroup',
            options={'ordering': ['name'], 'verbose_name': 'Группа товаров', 'verbose_name_plural': 'Группы товаров'},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ['name'], 'verbose_name': 'Единица измерения', 'verbose_name_plural': 'Единицы измерения'},
        ),
    ]
