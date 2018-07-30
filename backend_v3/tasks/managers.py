from django.db import models


class TaskManager(models.Manager):
	def list_tasks_on_projects(self, user, offset, first, sort_by, desc=False, filters=None):
		last = offset + first
		tasks = self.filter(project__gip=user)
		sort_field = None
		if sort_by == 'project':
			sort_field = models.F('project__number')
		elif sort_by == 'task':
			sort_field = models.F('name')
		if desc:
			sort_field = sort_field.desc()
		if filters.get('projects'):
			tasks = self.filter(project_id__in=filters['projects'])
		tc = tasks.count()
		if first < 0:
			last = tc
		if sort_field:
			tasks = tasks.order_by(sort_field, '-id')
		return tasks[offset:last], tc

	def list_tasks_in_report(self, user, filters=None):
		tasks = self.filter(project_id__in=filters['projects'])
		return tasks

