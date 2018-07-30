# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-11 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0031_auto_20180411_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='GOST',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'ГОСТ',
                'verbose_name_plural': 'ГОСТы',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='goodkind',
            name='analogs',
            field=models.ManyToManyField(blank=True, related_name='_goodkind_analogs_+', to='warehouse.GoodKind', verbose_name='Аналоги'),
        ),
        migrations.AddField(
            model_name='goodkind',
            name='gosts',
            field=models.ManyToManyField(blank=True, related_name='_goodkind_gosts_+', to='warehouse.GOST', verbose_name='ГОСТы'),
        ),
    ]
