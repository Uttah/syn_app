# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-17 07:31
from __future__ import unicode_literals

from django.db import migrations, connection


def migrate_clients(apps, schema_editor):
    CompaniesClient = apps.get_model('companies', 'Client')
    ClientsClient = apps.get_model('clients', 'Client')
    max_id = 0
    for c in CompaniesClient.objects.all():
        ClientsClient.objects.create(id=c.id, name=c.name)
        if max_id < c.id:
            max_id = c.id
    cursor = connection.cursor()
    cursor.execute("SELECT setval(%s, %s, True);", ['clients_client_id_seq', max_id + 1])
    cursor.fetchall()
    cursor.close()


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_auto_20180407_1637'),
    ]

    operations = [
        migrations.RunPython(
            migrate_clients
        )
    ]
