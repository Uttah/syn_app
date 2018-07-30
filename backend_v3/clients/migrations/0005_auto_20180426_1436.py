# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-26 11:36
from __future__ import unicode_literals

from django.db import migrations


def migrate_data(apps, scheme_editor):
    OrganizationForm = apps.get_model('clients', 'OrganizationForm')
    OrganizationForm.objects.create(name='ООО')
    OrganizationForm.objects.create(name='ОАО')
    OrganizationForm.objects.create(name='ЗАО')
    OrganizationForm.objects.create(name='ИП')
    OrganizationForm.objects.create(name='ГУП')
    OrganizationForm.objects.create(name='ИООО')
    OrganizationForm.objects.create(name='АО')
    OrganizationForm.objects.create(name='ПАО')
    OrganizationForm.objects.create(name='МУП')

class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_organizationform'),
    ]

    operations = [
        migrations.RunPython(
            migrate_data
        )
    ]