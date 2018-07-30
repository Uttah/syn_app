# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-18 12:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def default_units(apps, scheme_editor):
    all_good_kinds = apps.get_model('warehouse', 'GoodKind').objects.all()
    all_good = apps.get_model('warehouse', 'Good').objects.all().distinct('good_kind')
    for good_kind in all_good_kinds:
        for good in all_good:
            if good_kind.id == good.good_kind.id:
                good_kind.default_unit_id = good.unit_id
                good_kind.save()
    for good_kind in all_good_kinds:
        if not good_kind.default_unit_id:
            good_kind.default_unit_id = 1
            good_kind.save()


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0034_goodkind_default_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodkind',
            name='default_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.Unit', verbose_name='Ед. измерения по-умолчанию'),
        ),
        migrations.RunPython(
            default_units
        ),
    ]
