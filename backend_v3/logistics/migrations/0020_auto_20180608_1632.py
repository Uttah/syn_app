# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-08 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0019_logisticsrequestposition_delivery_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logisticstask',
            name='ready_for_work',
        ),
        migrations.AddField(
            model_name='logisticsrequest',
            name='ready_for_work',
            field=models.BooleanField(default=False, verbose_name='Передана логисту'),
        ),
    ]
