# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-16 09:21
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0008_auto_20180316_1809'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pressmark', models.CharField(max_length=100, verbose_name='Шифр')),
                ('object_name', models.CharField(max_length=1000, verbose_name='Название объекта')),
                ('section_name', models.CharField(max_length=1000, verbose_name='Название раздела')),
                ('organization', models.CharField(max_length=100, verbose_name='Организация')),
                ('document_name', models.CharField(max_length=1000, verbose_name='Название документа')),
                ('state', models.CharField(max_length=10, verbose_name='Стадия')),
                ('workers_data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('dates', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('editors', models.ManyToManyField(blank=True, related_name='_specification_editors_+', to=settings.AUTH_USER_MODEL, verbose_name='Редакторы')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project', verbose_name='Проект')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Создал')),
            ],
            options={
                'verbose_name': 'Спецификация',
                'verbose_name_plural': 'Спецификации',
            },
        ),
        migrations.CreateModel(
            name='SpecificationsPositions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description_info', models.CharField(blank=True, max_length=200, null=True, verbose_name='Тип, марка, обозначение документа, опросного листа')),
                ('positional_designation', models.CharField(max_length=100, null=True, verbose_name='Позиционное обозночение')),
                ('count', models.FloatField(null=True, verbose_name='Количество')),
                ('position_in_table', models.IntegerField(verbose_name='Положение в таблице')),
                ('grouping_name', models.CharField(max_length=100, null=True, verbose_name='Название группировки')),
                ('good_kind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.GoodKind', verbose_name='Вид товара')),
                ('specification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_specifications.Specification', verbose_name='Спецификация')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='warehouse.Unit', verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Позиция спецификации',
                'verbose_name_plural': 'Позиции спецификаций',
            },
        ),
    ]
