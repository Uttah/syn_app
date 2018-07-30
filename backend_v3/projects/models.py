from django.db import models
from .managers import ProjectManager, ProjectAnalysisSchemaManager


class State(models.Model):
	name = models.CharField('Название', max_length=100)
	letter = models.CharField('Буква', max_length=1)
	deleted = models.BooleanField('Удален', default=False)

	class Meta:
		verbose_name = 'Этап проекта'
		verbose_name_plural = 'Этапы проекта'
		ordering = ['name']

	def __str__(self):
		return self.name


class Project(models.Model):
	number = models.PositiveSmallIntegerField('Число', unique=True)
	description = models.CharField('Описание', max_length=512)
	gip = models.ForeignKey('users.User', related_name='project_gip', verbose_name='ГИП')
	state = models.ForeignKey('projects.State', verbose_name='Этап проекта')
	budget = models.IntegerField('Примерный бюджет', null=True, blank=True)
	customer = models.ForeignKey('clients.Client', on_delete=models.PROTECT, verbose_name='Заказчик', null=True, blank=True)
	manager = models.ForeignKey('users.User', related_name='project_manager', verbose_name='Менеджер', null=True, blank=True)
	user_created = models.ForeignKey('users.User', related_name='project_user_created', verbose_name='Создал', null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	comment = models.TextField('Комментарий', null=True, blank=True)

	objects = ProjectManager()

	class Meta:
		verbose_name = 'Проект'
		verbose_name_plural = "Проекты"
		ordering = ['number']
		permissions = (
			('global_analysis', 'Анализ всех проектов'),
			('change_project_state_batch', 'Изменять этап проекта в записях табеля'),
			('change_project_state', 'Может изменять этапы проекта в списке проектов')
		)

	def __str__(self):
		return '{:05d} - {}'.format(self.number, self.description)


class ProjectAnalysisSchema(models.Model):
	user_created = models.ForeignKey('users.User', verbose_name='Создал')
	name = models.CharField('Название', max_length=100)
	filters_schema = models.CharField('Схема', max_length=2048)

	objects = ProjectAnalysisSchemaManager()

	class Meta:
		unique_together = ('user_created', 'name')
		verbose_name = 'Схема фильтра анализа проектов'
		verbose_name_plural = 'Схемы фильтров анализа проектов'
		ordering = ('name',)

	def __str__(self):
		return self.name
