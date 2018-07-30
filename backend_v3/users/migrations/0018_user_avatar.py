# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-19 11:28
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_merge_20180413_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.avatar_directory_path, verbose_name='Аватар'),
        ),
    ]
