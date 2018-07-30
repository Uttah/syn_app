from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from .managers import SpecificationManager, SpecificationsPositionsManager
from django.contrib.contenttypes.fields import GenericRelation


class GOST(models.Model):
	name = models.CharField('Название', max_length=50, unique=True)

	class Meta:
		verbose_name = 'ГОСТ'
		verbose_name_plural = 'ГОСТы'
		ordering = ['name']

	def __str__(self):
		return self.name


class Specification(models.Model):
	user_created = models.ForeignKey('users.User', verbose_name='Создал')
	project = models.ForeignKey('projects.Project', verbose_name='Проект')
	editors = models.ManyToManyField('users.User', verbose_name='Редакторы', related_name='+', blank=True)
	pressmark = models.CharField('Шифр', max_length=100)
	object_name = models.CharField('Название объекта', max_length=1000)
	section_name = models.CharField('Название раздела', max_length=1000)
	organization = models.CharField('Организация', max_length=100)
	document_name = models.CharField('Название документа', max_length=1000)
	state = models.CharField('Стадия', max_length=10)
	workers_data = JSONField(null=True)
	dates = ArrayField(models.CharField(max_length=100), blank=True, null=True)
	approved = models.BooleanField('Утверждён', default=False)
	logistic_request = GenericRelation('logistics.LogisticsRequest', related_query_name='project_spec_reason')

	objects = SpecificationManager()

	class Meta:
		verbose_name = 'Спецификация'
		verbose_name_plural = 'Спецификации'

	def __str__(self):
		return '{:05d} - {}'.format(self.project.number, self.pressmark)


class SpecificationsPositions(models.Model):
	good_kind = models.ForeignKey('warehouse.GoodKind', on_delete=models.PROTECT, verbose_name='Вид товара', null=True)
	description_info = models.CharField('Тип, марка, обозначение документа, опросного листа', max_length=200, null=True,
	                                    blank=True)
	unit = models.ForeignKey('warehouse.Unit', on_delete=models.PROTECT, verbose_name='Единица измерения', null=True)
	specification = models.ForeignKey('project_specifications.Specification', verbose_name='Спецификация')
	positional_designation = models.CharField('Позиционное обозночение', max_length=100, null=True)
	count = models.FloatField('Количество', null=True)
	position_in_table = models.IntegerField('Положение в таблице')
	grouping_name = models.CharField('Название группировки', max_length=100, null=True)
	note = models.CharField('Комментарий', max_length=500, null=True)

	objects = SpecificationsPositionsManager()

	class Meta:
		verbose_name = 'Позиция спецификации'
		verbose_name_plural = 'Позиции спецификаций'
