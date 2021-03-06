# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-26 13:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20180424_1030'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Название')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='file',
            field=models.FileField(null=True, upload_to='', verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='document',
            name='number',
            field=models.CharField(default='Null', max_length=100, verbose_name='Номер документа'),
        ),
        migrations.AddField(
            model_name='document',
            name='document_kind',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.DocumentKind', verbose_name='Вид документа'),
        ),
    ]
