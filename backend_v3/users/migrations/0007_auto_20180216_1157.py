# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-16 08:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20180216_1155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coefficients',
            options={'ordering': ['user__last_name'], 'permissions': (('view_all_coefficients', 'Может просматривать и изменять все коэффициенты'), ('view_sub_coefficients', 'Может просматривать и изменять коэффициенты подчиненных')), 'verbose_name': 'Коэффициенты', 'verbose_name_plural': 'Коэффициенты'},
        ),
    ]