# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-28 07:37
from __future__ import unicode_literals

from django.db import migrations


def create_locations(apps, schema_editor):
    Location = apps.get_model('warehouse', 'Location')
    Project = apps.get_model('projects', 'Project')
    projects = Project.objects.all().prefetch_related('location_set')
    for p in projects:
        if not p.location_set.all():
            location_name = 'Склад "%05d"' % p.number
            Location.objects.create(name=location_name, project=p, user_id=120)


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0016_auto_20180327_1511'),
    ]

    operations = [
        migrations.RunPython(
            create_locations
        )
    ]
