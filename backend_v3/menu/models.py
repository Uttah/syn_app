from django.db import models
from django.contrib.auth.models import Permission


class MenuItem(models.Model):
	text = models.CharField('Название пункта', max_length=100)
	link = models.CharField('Ссылка', max_length=200)
	required_permissions = models.ManyToManyField(Permission, verbose_name='Разрешения для показа пункта меню', blank=True)
	sorting = models.PositiveSmallIntegerField('Значение сортировки')

	class Meta:
		verbose_name = 'Пункт меню'
		verbose_name_plural = 'Пункты меню'
		ordering = ('sorting',)

	def __str__(self):
		return '{} <{}> ({})'.format(self.text, self.link, self.sorting)


class TopMenu(models.Model):
	text = models.CharField('Текст заголовка', max_length=100)
	sorting = models.PositiveSmallIntegerField('Значение сортировки')
	items = models.ManyToManyField('menu.MenuItem', verbose_name='Пункты этого меню')
	position = models.ForeignKey('users.Position', verbose_name='Должность сотрудника с этим меню', null=True, blank=True)

	class Meta:
		verbose_name = 'Заголовок меню'
		verbose_name_plural = 'Заголовки меню'
		ordering = ('sorting',)

	def __str__(self):
		return '{} ({})'.format(self.text, self.sorting)
