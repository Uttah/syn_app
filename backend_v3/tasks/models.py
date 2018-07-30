from django.db import models
from tasks.managers import TaskManager


class Task(models.Model):
	name = models.CharField('Название', max_length=100)
	project = models.ForeignKey('projects.Project')

	objects = TaskManager()

	class Meta:
		unique_together = ('name', 'project')
		verbose_name = 'Задача'
		verbose_name_plural = 'Задачи'
		ordering = ['name']
