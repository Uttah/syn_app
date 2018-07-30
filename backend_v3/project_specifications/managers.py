from django.db import models


class SpecificationManager(models.Manager):

	def list_paged_specifications(self, user, offset, first, sort_by, desc=False, search=''):
		last = offset + first
		search = search.strip()
		filters = models.Q(project__gip=user) | models.Q(editors=user)
		specifications = self.filter(filters)
		if search != '':
			specifications = specifications.filter(models.Q(pressmark__icontains=search) |
								                             models.Q(object_name__icontains=search) |
								                             models.Q(organization__icontains=search) |
								                             models.Q(project__number__icontains=search))
		sort_keys = {
			None: 'project__number',
			'project': 'project__number',
			'pressmark': 'pressmark',
			'objectName': 'object_name',
			'sectionName': 'section_name',
			'organization': 'organization',
			'documentName': 'document_name',
			'state': 'state'
		}
		sort_field = models.F(sort_keys[sort_by])
		if desc:
			sort_field = sort_field.desc()
		specifications = specifications.order_by(sort_field, 'id').distinct(sort_keys[sort_by], 'id')
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = specifications.count()
		return specifications[offset:last], tc

	def load_good_kind(self, search='', require=[]):
		require_clause = models.Q(id__in=require)
		if search:
			_filter = models.Q(code__icontains=search) | models.Q(name__icontains=search)
			good_kinds = self.filter(_filter).union(self.filter(require_clause))
		else:
			good_kinds = self.filter()[:50].union(self.filter(require_clause))
		return good_kinds


class SpecificationsPositionsManager(models.Manager):

	def load_specifications_positions(self, info, filters=None):
		specifications_positions = self
		# Фильтрация по ID спецификации
		if not filters:
			return None
		specifications_positions = specifications_positions.filter(specification_id=filters).order_by(
			'position_in_table')
		for index in range(len(specifications_positions)):
			specifications_positions[index].position_in_table = index
		return specifications_positions

	def load_descriptions_info(self, info, filters=None):
		from warehouse.models import GoodKind
		specifications_positions = self.filter(good_kind_id=filters, description_info__isnull=False).distinct(
			'description_info').values('description_info')
		gosts = GoodKind.objects.filter(id=filters, gosts__isnull=False).distinct('gosts__name').values('gosts__name')
		descriptions_info = {s['description_info'] for s in specifications_positions}
		gosts = {g['gosts__name'] for g in gosts}
		gosts = sorted(list(gosts.union(descriptions_info)))
		return gosts
