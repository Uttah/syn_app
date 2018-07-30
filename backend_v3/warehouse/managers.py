from django.db import models
from django.contrib.postgres.search import SearchVector


class LocationManager(models.Manager):

	def load_warehouse(self, info, search=None, require=[], project=None):
		require_clause = models.Q(id__in=require)
		warehouses = self
		if project:
			warehouses = warehouses.filter(project_id=project)
		if search:
			try:
				search = int(search)
			except ValueError:
				pass
			warehouses = warehouses.filter(models.Q(name__icontains=search)).union(self.filter(require_clause))
		else:
			warehouses = warehouses.order_by('id')[:30].union(self.filter(require_clause))
		return warehouses


class GoodManager(models.Manager):

	def list_paged_goods(self, info, offset, first, sort_by, desc=False, search='', filters=None):
		from .schema.types import GoodSubRowsType
		from .schema.types import TableGoodType
		user = info.context.user
		goods = self.filter()
		if not user.has_perm('users.view_warehouse'):
			goods = goods.exclude(location_id=646)
		search = search.strip()
		if search != '':
			_filter = models.Q(good_kind__code__icontains=search) | models.Q(search=search)
			goods = goods.annotate(search=SearchVector('good_kind__name', 'good_kind__manufacturer__name', config='russian'))
			goods = goods.filter(_filter)
		sorts = {
			'goodGroup': 'good_kind__good_group__name',
			'code': 'good_kind__code',
			'name': 'good_kind__name',
			'manufacturer': 'good_kind__manufacturer__name'
		}
		if sort_by is None or sort_by not in sorts:
			sort_by = 'goodGroup'
		sort_field = models.F(sorts[sort_by])
		if desc:
			sort_field = sort_field.desc()
		if filters:
			if filters.get('manufacturer'):
				goods = goods.filter(good_kind__manufacturer__id=filters['manufacturer'])
			if filters.get('storage'):
				goods = goods.filter(location__id=filters['storage'])
			if filters.get('responsible'):
				goods = goods.filter(responsible__id=filters['responsible'])
			if filters.get('project'):
				goods = goods.filter(project__id=filters['project'])
			if filters.get('quantity') and filters.get('quantity_type'):
				if filters['quantity_type'] == 'equal':
					goods = goods.filter(count=filters['quantity'])
				if filters['quantity_type'] == 'gte':
					goods = goods.filter(count__gte=filters['quantity'])
				if filters['quantity_type'] == 'lte':
					goods = goods.filter(count__lte=filters['quantity'])
		# Объединяем good'ы по goodKind'ам
		row_counter = goods.values('good_kind_id').annotate(num_goods=models.Count('id')).order_by(sort_field)
		# begin - количество good которые идут ДО и не попадают в эту страницу
		begin = row_counter[:offset].aggregate(models.Sum('num_goods'))['num_goods__sum']
		if begin is None:
			begin = 0
		# end - количество good которые идут ПОСЛЕ и не попадают в эту страницу
		end = row_counter[offset:offset + first].aggregate(models.Sum('num_goods'))['num_goods__sum']
		if end is None:
			end = 0

		end = end + begin
		# sorted_goods - все goods'ы на этой странице
		sorted_goods = goods.order_by(sort_field)[begin:end]
		rows = []
		sub_rows = []

		if len(sorted_goods):
			current_good_kind = sorted_goods[0].good_kind
		else:
			return [], 0
		for item_good in sorted_goods:
			if item_good.good_kind != current_good_kind:
				good_type = TableGoodType(good_kind=current_good_kind, sub_rows=sub_rows)
				rows.append(good_type)
				current_good_kind = item_good.good_kind
				sub_rows = []
			good_sub = GoodSubRowsType(
				id=item_good.id,
				location=item_good.location,
				count=item_good.count,
				unit=item_good.unit,
				project=item_good.project,
				responsible=item_good.responsible,
				note=item_good.note,
				defect=item_good.defect)
			sub_rows.append(good_sub)
		good_type = TableGoodType(good_kind=current_good_kind, sub_rows=sub_rows)
		rows.append(good_type)
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		return rows, goods.aggregate(models.Count('good_kind_id', distinct=True))['good_kind_id__count']

	def checking_manufacturer(self, filters=None):
		# Фильтр по id производителя
		goods = self.filter(good_kind__manufacturer__id=filters['manufacturer'])
		if goods:
			can_delete_it = False
		else:
			can_delete_it = True
		return can_delete_it


class ManufacturerManager(models.Manager):

	def list_paged_manufacturer(self, offset, first, sort_by, search='', desc=False):
		last = offset + first
		search = search.strip()
		manufacturers = self.filter()
		sort_field = models.F('name')
		if desc:
			sort_field = sort_field.desc()
		manufacturers = manufacturers.order_by(sort_field)
		if search != '':
			manufacturers = manufacturers.filter(name__icontains=search)
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = manufacturers.count()
		return manufacturers[offset:last], tc


class GoodKindManager(models.Manager):

	def list_paged_goods_kinds(self, offset, first, sort_by, desc=False, search='', filters=None):
		last = offset + first
		search = search.strip()
		good_kinds = self.filter()
		if search != '':
			_filter = models.Q(code__icontains=search) | models.Q(search=search)
			good_kinds = self.annotate(search=SearchVector('name', 'manufacturer__name', 'gosts__name', config='russian'))
			good_kinds = good_kinds.filter(_filter)
		if filters:
			if filters.get('only_new', False):
				good_kinds = good_kinds.filter(new=filters['only_new'])
			if filters.get('manufacturer_id'):
				good_kinds = good_kinds.filter(manufacturer_id__in=filters['manufacturer_id'])
			if filters.get('groups_id'):
				good_kinds = good_kinds.filter(good_group_id__in=filters['groups_id'])
		sort_field = None
		if sort_by == 'code' or sort_by is None:
			sort_field = models.F('code')
		elif sort_by == 'name':
			sort_field = models.F('name')
		elif sort_by == 'manufacturer':
			sort_field = models.F('manufacturer')
		if desc:
			sort_field = sort_field.desc()
		good_kinds = good_kinds.order_by(sort_field)
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = good_kinds.count()
		return good_kinds[offset:last], tc

	def load_good_kind(self, search='', require=[], checked=False):
		require_clause = models.Q(id__in=require)
		if search:
			_filter = models.Q(code__icontains=search) | models.Q(name__icontains=search)
			good_kinds = self.filter(_filter).union(self.filter(require_clause))
		else:
			good_kinds = self.filter()[:50].union(self.filter(require_clause))
		if checked:
			good_kinds = self.filter(new=False)
		return good_kinds
