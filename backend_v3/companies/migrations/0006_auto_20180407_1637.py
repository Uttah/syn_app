# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-07 13:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_auto_20180306_1219'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ('client__name',), 'verbose_name': 'компания', 'verbose_name_plural': 'компании'},
        ),
        migrations.RemoveField(
            model_name='company',
            name='name',
        ),
        migrations.RemoveField(
            model_name='company',
            name='requisites',
        ),
        migrations.AddField(
            model_name='company',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='companies.Client', verbose_name='Контрагент'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='minimize_salary',
            field=models.BooleanField(default=False, verbose_name='Минимизировать ЗП'),
        ),
        migrations.AddField(
            model_name='company',
            name='rest_as_gray',
            field=models.BooleanField(default=False, verbose_name='Остальное - наличными'),
        ),
    ]