from django.contrib.auth.models import BaseUserManager
from django.db.models.functions import Lower
from django.db.models import F, Q, Manager


class UserManager(BaseUserManager):
	# noinspection PyMethodMayBeStatic
	def create_user(self, **kwargs):
		password = kwargs['password']
		del kwargs['password']
		new_user = self.create(**kwargs)
		new_user.set_password(password)
		new_user.save()

	def create_superuser(self, **kwargs):
		self.create_user(**kwargs)

	def list_all_users(self, info, search='', subordinate=False):
		if subordinate:
			user = info.context.user
			users = self.filter(last_name__icontains=search, fired=False, head=user.id)
			return users
		return self.filter(last_name__icontains=search, fired=False)

	def list_paged_users(self, offset, first, sort_by, desc=False, search='', filters=None, show_fired=False):
		search = search.strip()
		fields = (Lower('last_name'), Lower('first_name'), Lower('patronym'))
		if desc:
			fields = (field.desc() for field in fields)
		_filters = Q(last_name__icontains=search) | Q(first_name__icontains=search) | Q(patronym__icontains=search) | \
							Q(personal_phone__icontains=search) | Q(work_phone__icontains=search) | Q(email__icontains=search)
		if not show_fired:
			_filters = _filters & Q(fired=False)
		users = self.order_by(*fields).filter(_filters)
		last = offset + first
		if search != '' or not show_fired:
			tc = users.count()
		else:
			tc = self.count()
		if first < 0:
			last = tc
		return users[offset:last], tc


class OccupationManager(Manager):
	def list_paged_occupations(self, offset, first, sort_by, desc=False, search='', filters=None):
		renames = {
			'user': ('user__last_name', 'user__first_name', 'user__patronym'),
			'mainCompany': ('main_company__client__name',),
			'positions': ('user__positions__name',),
			'salary': ('salary',),
			'base': ('base',),
			'advance': ('advance',),
			'fixedHour': ('fixed_hour',),
			'byHours': ('by_hours',),
			'transportation': ('transportation',)
		}
		search = search.strip()
		show_fired = search != ''
		sort_by = renames.get(sort_by, (sort_by,))
		fields = (F(field) for field in sort_by)
		if desc:
			fields = (field.desc() for field in fields)
		filters_renames = {
			'companies': 'main_company_id',
			'positions': 'user__positions__id'
		}
		_filter = (Q(user__last_name__icontains=search) | Q(user__first_name__icontains=search))
		if not show_fired:
			_filter = _filter & Q(user__fired=False)
		if filters is not None:
			for k, v in filters.items():
				filtered_key = filters_renames.get(k, None)
				if filtered_key is not None and v is not None and len(v) > 0:
					filtered_key = filtered_key + '__in'
					_filter &= Q(**{filtered_key: v})
		occupations = self.order_by(*fields).filter(_filter).select_related('user', 'main_company__client')
		last = offset + first
		if first < 0:
			return [], 0
		if search != '' or filters is not None:
			tc = occupations.count()
		else:
			tc = self.count()
		return occupations[offset:last], tc
