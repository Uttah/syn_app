# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-01 14:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('salary', '0005_auto_20180124_1236'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('value', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Значение')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник')),
            ],
        ),
    ]