from django.db import models


class ProjectManager(models.Manager):
	def load_projects(self, info, search=None, gip=None, current_gip=None, require=None):
		# Создаем Q-объект для безусловной выборки указанных в require проектов
		require_clause = None
		if require is not None and len(require) > 0:
			require_clause = models.Q(id__in=require)
		# Возвращаем проекты конкретного ГИПа
		projects = self
		if gip:
			if require_clause:
				projects = projects.filter(models.Q(gip_id=gip) | require_clause)
			else:
				projects = projects.filter(gip_id=gip)
		# Если передан параметр показывать пректы ТОЛЬКО Главного Инженера Проекта
		if current_gip:
			projects = projects.filter(gip=info.context.user)
		# Возвращаем проекты по поисковой строке
		if search:
			try:
				search = int(search)
			except ValueError:
				pass
			if require_clause:
				projects = projects.filter(
					models.Q(number__icontains=search) | models.Q(description__icontains=search) | require_clause)
			else:
				projects = projects.filter(models.Q(number__icontains=search) | models.Q(description__icontains=search))
		else:
			if require_clause:
				projects = projects.filter(require_clause).union(projects.order_by('number')[:50])
			else:
				projects = projects.order_by('number')[:50]
		return projects

	def paged_projects(self, offset, first, sort_by, search='', desc=False, filters=None):
		last = offset + first
		search = search.strip()
		projects = self.filter()
		if search:
			projects = self.filter(models.Q(number__icontains=search) | models.Q(description__icontains=search) | models.Q(
				comment__icontains=search) | models.Q(customer__name__icontains=search))
		sort_field = models.F('number')
		if sort_by == 'customer':
			sort_field = models.F('customer__name')
		elif sort_by == 'state':
			sort_field = models.F('state__name')
		if desc:
			sort_field = sort_field.desc()
		if filters:
			if filters.get('gip'):
				projects = projects.filter(gip_id=filters['gip'])
			if filters.get('state'):
				projects = projects.filter(state_id=filters['state'])
			if filters.get('manager'):
				projects = projects.filter(manager_id=filters['manager'])
			if filters.get('customer'):
				projects = projects.filter(customer_id=filters['customer'])
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = projects.count()
		projects = projects.order_by(sort_field)
		return projects[offset:last], tc


class ProjectAnalysisSchemaManager(models.Manager):
	def load_schemas(self, user):
		schemas = self.filter(user_created_id=user)
		return schemas
