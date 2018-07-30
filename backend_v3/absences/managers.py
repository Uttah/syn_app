from django.db.models import F, Q, Manager


class AbsenceManager(Manager):
	def list_paged_absences(self, info, offset, first, sort_by, desc=False, search='', filters=None):
		user = info.context.user
		absences = self
		renames = {
			'worker': ('worker__last_name', 'worker__first_name', 'worker__patronym'),
			'date': ('begin', 'end', 'worker__last_name', 'worker__first_name', 'worker__patronym'),
			'reason': ('reason__name',)
		}
		sort_by = renames.get(sort_by, (sort_by,))
		fields = (F(field) for field in sort_by)
		if desc:
			fields = (field.desc() for field in fields)
		filters_renames = {
			'reason': 'reason_id'
		}
		_filter = Q(worker__fired=False)
		if not user.has_perm('absences.manage_absences'):
			_filter &= Q(worker__head=user)

		if filters is not None:
			for k, v in filters.items():
				filtered_key = filters_renames.get(k, None)
				if filtered_key is not None and len(v) > 0:
					filtered_key = filtered_key + '__in'
					_filter &= Q(**{filtered_key: v})
		absences = filters.get('date_range').get_two_date_range(absences, 'begin', 'end')
		absences = absences.select_related('worker', 'reason', 'user_added').filter(_filter).order_by(*fields)
		last = offset + first
		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = absences.count()
		return absences[offset:last], tc

