# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-04 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0019_goodposition_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodposition',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='warehouse.Unit', verbose_name='Единица измерения'),
        ),
    ]