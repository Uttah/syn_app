# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-27 10:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0005_auto_20180427_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logisticsrequest',
            name='responsible',
            field=models.ManyToManyField(related_name='LogisticsRequest_responsible', to=settings.AUTH_USER_MODEL, verbose_name='Ответственные'),
        ),
    ]
