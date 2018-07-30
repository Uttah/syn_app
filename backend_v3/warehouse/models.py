from django.db import models
from .managers import GoodManager, ManufacturerManager, GoodKindManager, LocationManager


class Manufacturer(models.Model):
	name = models.CharField('Название', max_length=250, unique=True)

	objects = ManufacturerManager()

	class Meta:
		verbose_name = 'Производитель'
		verbose_name_plural = 'Производители'
		ordering = ['name']

	def __str__(self):
		return self.name


class Unit(models.Model):
	name = models.CharField('Единица измерения', max_length=50)
	short_name = models.CharField('Сокращение', max_length=20, unique=True)
	restrict_sum = models.BooleanField('Не суммировать', default=False)

	class Meta:
		ordering = ['name']
		verbose_name = 'Единица измерения'
		verbose_name_plural = 'Единицы измерения'

	def __str__(self):
		return self.name


class GoodGroup(models.Model):
	name = models.CharField('Название', max_length=500)
	parent_group = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True,
	                                 verbose_name='Родительская группа')

	class Meta:
		ordering = ['name']
		verbose_name = 'Группа товаров'
		verbose_name_plural = 'Группы товаров'

	def __str__(self):
		return self.name


class GoodKind(models.Model):
	code = models.CharField('Артикул', max_length=100, null=True, blank=True)
	name = models.TextField('Название')
	manufacturer = models.ForeignKey('warehouse.Manufacturer', on_delete=models.PROTECT, verbose_name='Производитель')
	mass = models.FloatField('Масса 1 ед. в кг.', null=True, blank=True)
	good_group = models.ForeignKey('warehouse.GoodGroup', null=True, blank=True, verbose_name='Группа товаров')
	analogs = models.ManyToManyField('self', verbose_name='Аналоги', blank=True, symmetrical=False)
	gosts = models.ManyToManyField('project_specifications.GOST', verbose_name='ГОСТы', related_name='+', blank=True)
	new = models.BooleanField('Новый', default=True)
	default_unit = models.ForeignKey('warehouse.Unit', verbose_name='Ед. измерения по-умолчанию', null=True)
	confirmed = models.ForeignKey('users.User', verbose_name='Кто подтвердил', null=True)

	objects = GoodKindManager()

	class Meta:
		verbose_name = 'Вид товара'
		verbose_name_plural = 'Виды товара'
		unique_together = ('code', 'manufacturer')
		permissions = (
			('can_moderate', 'Может подтверждать виды товаров'),
		)

	def __str__(self):
		if self.code is None:
			code = 'б/а'
		else:
			code = self.code
		return '{} - {} ({})'.format(code, self.name, self.manufacturer)


class Location(models.Model):
	name = models.CharField('Название', max_length=50)
	project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, verbose_name='Проект', null=True,
	                            blank=True)
	responsible = models.ForeignKey('users.User', verbose_name='Ответственный', null=True)

	objects = LocationManager()

	class Meta:
		verbose_name = 'Склад'
		verbose_name_plural = 'Склады'

	def __str__(self):
		return self.name


class Good(models.Model):
	good_kind = models.ForeignKey('warehouse.GoodKind', on_delete=models.PROTECT, verbose_name='Вид товара')
	location = models.ForeignKey('warehouse.Location', on_delete=models.PROTECT, verbose_name='Местонахождение')
	count = models.FloatField('Количество')
	unit = models.ForeignKey('warehouse.Unit', on_delete=models.PROTECT, verbose_name='Единица измерения')
	note = models.CharField('Примечание', max_length=250, null=True, blank=True)
	project = models.ForeignKey('projects.Project', null=True, blank=True, verbose_name='Назначение')
	defect = models.BooleanField('Некондиция', default=False)
	responsible = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name='Ответственный')

	objects = GoodManager()

	class Meta:
		verbose_name = 'Товар'
		verbose_name_plural = 'Товары'

	def __str__(self):
		return '{} {} {} на {}'.format(self.good_kind, self.count, self.unit, self.location)
