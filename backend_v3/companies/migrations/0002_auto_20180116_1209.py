# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-16 09:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='requisites',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Requisites', verbose_name='Реквизиты'),
        ),
        migrations.AlterField(
            model_name='company',
            name='short_name',
            field=models.CharField(max_length=5, null=True, verbose_name='Сокращенное название (аббревиатура)'),
        ),
    ]