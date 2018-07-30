import math
from datetime import datetime, date
from calendar import monthrange
from django.db import models
from django.db.models.functions import Cast
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions.datetime import Extract, TruncMonth
from django.contrib.postgres.aggregates import StringAgg
from salary.models import DayOff
from users.models import User
from absences.models import Absence
from projects.models import Project
from graphene.utils.str_converters import to_snake_case
from projects.analyze import get_class_hierarchy
from synergycrm.exceptions import SngyException


class ReportManager(models.Manager):
	def list_paged_reports(self, offset, first, user, sort_by, gip=False, desc=False, search='', filters=None):
		last = offset + first
		search = search.strip()
		if gip:
			if filters.get('only_own_projects', True):
				reports = self.filter(projects__gip=user).distinct()
			else:
				reports = self.filter()
		else:
			reports = self.filter(models.Q(user_added=user) | models.Q(worker=user))
		sort_field = None
		if sort_by == 'worker':
			sort_field = models.F('worker')
		elif sort_by == 'projectNum':
			reports = reports.annotate(min=models.Min('projects__number')).order_by('min')
		elif sort_by == 'reportDate':
			sort_field = models.F('report_date')
		if desc:
			if sort_by != 'projectNum':
				sort_field = sort_field.desc()
			else:
				reports = reports.annotate(min=models.Min('projects__number')).order_by('-min')
		if search != '':
			reports = reports.filter(task__icontains=search)
		if filters:
			if filters.get('date_range'):
				if gip:
					unverified_reports = reports.filter(deleted=False, checked_by=None)
				reports = filters.get('date_range').get_range(reports, 'report_date')
				if gip:
					reports = reports | unverified_reports
			if filters.get('worker'):
				reports = reports.filter(worker_id=filters['worker'])
			if filters.get('projects'):
				reports = reports.filter(projects__in=filters['projects']).distinct()
			if filters.get('state'):
				reports = reports.filter(projectstate__state_id=filters['state'])
			if filters.get('func_role'):
				reports = reports.filter(func_role_id=filters['func_role'])
			if filters.get('process'):
				reports = reports.filter(process_id=filters['process'])
				if filters.get('sub_process'):
					reports = reports.filter(process_id=filters['process'], sub_process_id=filters['sub_process'])

		# Больше не позволяем просматривать таблицы полностью
		if first < 0:
			return [], 0
		tc = reports.count()
		if sort_field:
			reports = reports.order_by(sort_field, '-id')
		if gip and sort_field:
			reports = reports.annotate(checked=Cast('checked_by_id', models.BooleanField())). \
				order_by('-checked', 'deleted', sort_field, 'worker__last_name', '-id')
		return reports[offset:last], tc

	def sum_hours(self, user, _date):
		year = int('20' + _date[-2:])
		month = int(_date[:-2])
		date1 = datetime(year, month, 1)
		date2 = date1.replace(day=monthrange(year, month)[1])
		reports = self.filter(worker_id=user.id, report_date__range=(date1, date2)).exclude(deleted=True)
		reports = reports.values('report_date').annotate(sum=models.Sum('time_spent'))
		projects = reports.values('report_date').annotate(projects=StringAgg(
			Cast('projects__number', models.CharField(max_length=10)), delimiter=', ', distinct=True))
		for r in reports:
			for p in projects:
				if r['report_date'] == p['report_date']:
					r['projects'] = p['projects']
		day_off_all = [v['date'] for v in DayOff.objects.filter(date__range=(date1, date2)).values('date')]
		for r in reports:
			r['day_off'] = r['report_date'] in day_off_all
		month_sum = reports.aggregate(month_sum=models.Sum('sum'))['month_sum']
		if month_sum:
			month_sum = month_sum.total_seconds() / 3600
		else:
			month_sum = 0
		month_sum = "{0:.2f}".format(month_sum)
		return reports, month_sum

	def sum_projects(self, user, _date):
		year = int('20' + _date[-2:])
		month = int(_date[:-2])
		date1 = datetime(year, month, 1)
		date2 = date1.replace(day=monthrange(year, month)[1])
		reports = self.filter(worker_id=user.id, report_date__range=(date1, date2)).exclude(deleted=True)
		sub_query = self.filter(id=OuterRef('id')).annotate(count=models.Count('projects__number')).values('count')
		return reports.values('projects__number', 'projects__description'). \
			annotate(sum=models.Sum(Extract('time_spent', 'EPOCH') / Subquery(sub_query),
		                          output_field=models.FloatField()) / 3600).order_by('projects__number')

	def fillouts(self, _date, paged):
		year = int('20' + _date[-2:])
		month = int(_date[:-2])
		now = datetime.now()
		if now.month == month:
			last_day = now.day
		else:
			last_day = monthrange(year, month)[1]
		month_days = [date(year, month, i + 1) for i in range(last_day)]
		days_off = DayOff.objects.filter(date__range=(month_days[0], month_days[-1])).values('date')
		days_off = [d['date'] for d in days_off]
		working_days = list(set(month_days) - set(days_off))
		working_days_len = len(working_days)

		users_objects = User.objects.filter(fired=False)
		users = {}
		users_working_days_len = {}
		min_working_day = min(working_days)
		for u in users_objects:
			user_occupation = u.occupation
			# Смотрим не был ли сотрудник принят в рассматриваемом месяце.
			# Если да, то не учитываем для него дни, которые были до даты его принятия.
			if u.hire_date > min_working_day:
				users[u.id] = [d for d in working_days if d >= u.hire_date]
				w_days_len = len(users[u.id])
			else:
				users[u.id] = working_days[:]
				w_days_len = working_days_len
			days_are_needed = math.ceil(w_days_len * user_occupation.fraction / 100)
			users_working_days_len[u.id] = days_are_needed

		reports = self.filter(report_date__range=(month_days[0], month_days[-1])).distinct('worker_id', 'report_date')
		absences = Absence.objects.filter(begin__lte=month_days[-1], end__gte=month_days[0])

		for u in users:
			for r in reports:
				for day in users[u][:]:
					if r.worker_id == u:
						if r.report_date == day:
							try:
								users[u].remove(day)
							except ValueError:
								pass

			for a in absences:
				for day in users[u][:]:
					if a.worker_id == u:
						if a.begin <= day <= a.end:
							try:
								users[u].remove(day)
							except ValueError:
								pass

		for u in users:
			users[u] = len(users[u])

		users_short_names = {u.id: u.short_name for u in users_objects}
		users_type = []
		for u in users:
			has_work_days = users_working_days_len[u] - users[u]
			days_missing = users[u]
			if has_work_days < 0:
				days_missing = 0
				has_work_days *= -1
			users_type.append(
				{'short_name': users_short_names[u], 'days_missing': days_missing, 'has_work_days': has_work_days})

		key = to_snake_case(paged['sort_by'])
		users_type.sort(key=lambda i: i[key], reverse=paged['desc'])
		last = paged['offset'] + paged['first']
		tc = len(users_type)
		if paged['first'] < 0:
			last = tc

		return users_type[paged['offset']:last], tc

	def project_analyze(self, user, filters, limits):
		if len(filters) < 1:
			return None

		mapping = {
			'worker': 'worker_id',
			'project': 'projects__id',
			'process': 'process_id',
			'subProcess': 'sub_process_id',
			'funcRole': 'func_role_id',
			'place': 'place_id',
			'projectState': 'projectstate__state_id',
			'date': ''    # Обрабатывается отдельно
		}
		value_fields = []
		user_projects_ids = [d['id'] for d in Project.objects.filter(gip=user).values('id')]
		filtered = self.filter(deleted=False, checked_by__isnull=False)
		filtered = limits.get_range(filtered, 'report_date')

		if not user.has_perm('projects.global_analysis') and not user_projects_ids:
			raise SngyException('Отсутствуют проекты, в которых вы являетесь ГИПом!')

		if not user.has_perm('projects.global_analysis'):
			project_filter = [f for f in filters if f['name'] == 'project']
			if project_filter:
				project_filter = project_filter[0]
				project_filter.filter = [id for id in project_filter.filter if id in user_projects_ids]
				if not project_filter.filter:
					project_filter.filter = user_projects_ids
			else:
				filtered = filtered.filter(projects__id__in=user_projects_ids)

		for f in filters:
			if len(f.filter) > 0:
				field_name = mapping[f.name] + '__in'
				filtered = filtered.filter(models.Q(**{field_name: f.filter}))
			if mapping[f.name]:
				value_fields.append(mapping[f.name])

		# Для вычисления стоимости часов нам все равно необходимо сгруппировать сотрудников
		worker_mapping = mapping['worker']
		if worker_mapping not in value_fields:
			value_fields.append(worker_mapping)

		sub_query = self.filter(id=OuterRef('id')).annotate(count=models.Count('projects__number')).values('count')
		hour_sum = models.Sum(Extract('time_spent', 'EPOCH') / Subquery(sub_query), output_field=models.FloatField()) / 3600
		values = filtered.values(*value_fields)
		result = values.annotate(hours=hour_sum, mnth=TruncMonth('report_date')).order_by(*value_fields)

		root_class = get_class_hierarchy([(f.name, mapping[f.name]) for f in filters])
		root_class.append(result)
		root_class.get_totals()
		return root_class.storage
