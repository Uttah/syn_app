# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-23 10:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0014_auto_20180323_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodkind',
            name='analogs',
            field=models.ManyToManyField(blank=True, null=True, related_name='_goodkind_analogs_+', to='warehouse.GoodKind', verbose_name='Аналоги'),
        ),
    ]