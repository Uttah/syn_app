# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-02 11:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_created=True, verbose_name='Дата создания')),
                ('text', models.CharField(max_length=500, verbose_name='Текст уведомления')),
                ('confirmed', models.BooleanField(default=False)),
                ('created', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_created_user', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
                ('purpose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_purpose_user', to=settings.AUTH_USER_MODEL, verbose_name='Цель')),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
            },
        ),
    ]
