# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-30 19:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0036_location_responsible'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logistics', '0007_auto_20180427_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Good', verbose_name='Складская позиция')),
                ('logistics_request_position', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='logistics.LogisticsRequestPosition', verbose_name='Заявочная позиция')),
            ],
            options={
                'verbose_name': 'Позиция перемещения',
                'verbose_name_plural': 'Позиции перемещений',
                'ordering': ['good'],
            },
        ),
        migrations.CreateModel(
            name='TransferRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ready_to_go', models.BooleanField(verbose_name='Готова к выполнению')),
                ('creation_date', models.DateField(verbose_name='Дата создания')),
                ('where', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.Location', verbose_name='Куда')),
                ('who_requested', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Кто запросил')),
            ],
            options={
                'verbose_name': 'Заявка на перемещение',
                'verbose_name_plural': 'Заявки на перемещени',
                'ordering': ['who_requested'],
            },
        ),
        migrations.AddField(
            model_name='transferposition',
            name='transfer_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logistics.TransferRequest', verbose_name='Заявка на перемещение'),
        ),
    ]
