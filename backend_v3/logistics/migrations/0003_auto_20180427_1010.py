# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-27 07:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_auto_20180426_1634'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('warehouse', '0035_auto_20180424_1811'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logistics', '0002_positionrequest_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogisticsRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when_requested', models.DateField(verbose_name='Когда потребовал')),
                ('deadline', models.DateField(verbose_name='Крайний срок')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('responsible', models.ManyToManyField(related_name='LogisticsRequest_responsible', to=settings.AUTH_USER_MODEL, verbose_name='Ответственные')),
                ('who_requested', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Кто потребовал')),
            ],
            options={
                'verbose_name': 'Заявка на закупку',
                'verbose_name_plural': 'Заявки на закупки',
                'ordering': ['when_requested'],
            },
        ),
        migrations.CreateModel(
            name='LogisticsRequestPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='Номер п/п')),
                ('count', models.FloatField(verbose_name='Необходимое количество')),
                ('order_date', models.DateField(blank=True, null=True, verbose_name='Дата заказа')),
                ('expected_date', models.DateField(blank=True, null=True, verbose_name='Ожидаемая дата поставки')),
                ('deadline', models.DateField(verbose_name='Необходимая дата поставки')),
                ('finished_date', models.DateField(blank=True, null=True, verbose_name='Фактическая дата выполнения')),
                ('canceled', models.BooleanField(default=False, verbose_name='Отменено')),
                ('canceled_position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='logistics.LogisticsRequestPosition', verbose_name='Отмененная позиция')),
                ('good_kind', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='warehouse.GoodKind', verbose_name='Вид товара')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='logistics.LogisticsRequest', verbose_name='Заявка на закупку')),
            ],
            options={
                'verbose_name': 'Заявочная позиция',
                'verbose_name_plural': 'Заявочные позиции',
                'ordering': ['request__when_requested', 'number'],
            },
        ),
        migrations.CreateModel(
            name='LogisticsTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(verbose_name='Дата формирования')),
                ('files', models.ManyToManyField(blank=True, to='documents.Document')),
                ('responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Ответственный')),
            ],
            options={
                'verbose_name': 'Задача на закупку',
                'verbose_name_plural': 'Задачи на закупки',
                'ordering': ['created_date'],
            },
        ),
        migrations.RemoveField(
            model_name='buyrequisition',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='buyrequisition',
            name='responsible',
        ),
        migrations.RemoveField(
            model_name='buyrequisition',
            name='who_requested',
        ),
        migrations.RemoveField(
            model_name='buytask',
            name='files',
        ),
        migrations.RemoveField(
            model_name='buytask',
            name='responsible',
        ),
        migrations.RemoveField(
            model_name='positionrequest',
            name='buy_requisition',
        ),
        migrations.RemoveField(
            model_name='positionrequest',
            name='buy_task',
        ),
        migrations.RemoveField(
            model_name='positionrequest',
            name='canceled_position',
        ),
        migrations.RemoveField(
            model_name='positionrequest',
            name='good_kind',
        ),
        migrations.RemoveField(
            model_name='positionrequest',
            name='unit',
        ),
        migrations.DeleteModel(
            name='BuyRequisition',
        ),
        migrations.DeleteModel(
            name='BuyTask',
        ),
        migrations.DeleteModel(
            name='PositionRequest',
        ),
        migrations.AddField(
            model_name='logisticsrequestposition',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='logistics.LogisticsTask', verbose_name='Задача на закупку'),
        ),
        migrations.AddField(
            model_name='logisticsrequestposition',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='warehouse.Unit', verbose_name='Единица измерения'),
        ),
    ]
